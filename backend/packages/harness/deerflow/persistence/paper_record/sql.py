"""Paper Record 的 SQLAlchemy 仓储实现。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deerflow.persistence.paper_record.model import PaperRecordRow
from deerflow.utils.time import coerce_iso


@dataclass(slots=True, frozen=True)
class PaperRecordUpsertResult:
    """描述一次 upsert 是否新建了 Paper Record。"""

    created: bool
    record: dict[str, Any]


class PaperRecordRepository:
    """提供 Paper Record 的 upsert/list/get 访问面。"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    @staticmethod
    def _paper_id_for(user_id: str, source_name: str, source_paper_id: str) -> str:
        """为同一用户下的 source/id 对生成稳定 Paper Record ID。"""
        return uuid5(NAMESPACE_URL, f"{user_id}:{source_name}:{source_paper_id}").hex

    @staticmethod
    def _coerce_datetime(value: datetime) -> str:
        """把 SQLite 可能丢失时区的时间戳统一转成 ISO 字符串。"""
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return coerce_iso(value)

    @staticmethod
    def _merge_unique_strings(existing: list[str], additions: list[str]) -> list[str]:
        """保留原顺序合并字符串列表，避免 JSON 字段产生重复值。"""
        merged = list(existing)
        seen = set(existing)
        for item in additions:
            if not item or item in seen:
                continue
            merged.append(item)
            seen.add(item)
        return merged

    @classmethod
    def _row_to_dict(cls, row: PaperRecordRow) -> dict[str, Any]:
        """把 ORM 行对象转换成 API 友好的扁平字典。"""
        data = row.to_dict()
        data["authors"] = data.pop("authors_json") or []
        data["categories"] = data.pop("categories_json") or []
        data["discovered_watch_ids"] = data.pop("discovered_watch_ids_json") or []
        data["matched_query_terms"] = data.pop("matched_query_terms_json") or []
        data.pop("raw_source_json", None)
        data["created_at"] = cls._coerce_datetime(row.created_at)
        data["updated_at"] = cls._coerce_datetime(row.updated_at)
        return data

    @staticmethod
    def _set_if_changed(row: PaperRecordRow, field_name: str, value: Any) -> bool:
        """仅在字段值真正变化时写回，避免重复 run 产生无意义更新时间。"""
        if getattr(row, field_name) == value:
            return False
        setattr(row, field_name, value)
        return True

    async def upsert_paper(
        self,
        *,
        user_id: str,
        watch_id: str,
        source_name: str,
        source_paper_id: str,
        title: str,
        abstract: str,
        authors: list[str],
        categories: list[str],
        matched_query_terms: list[str],
        published_at: str | None,
        source_updated_at: str | None,
        source_abs_url: str,
        source_pdf_url: str | None,
        pdf_status: str,
        pdf_relative_path: str | None,
        pdf_error: str | None,
        raw_source: dict[str, object],
    ) -> PaperRecordUpsertResult:
        """按 ``(user_id, source_name, source_paper_id)`` 幂等 upsert 一篇论文。"""
        paper_id = self._paper_id_for(user_id, source_name, source_paper_id)
        async with self._sf() as session:
            existing = await session.get(PaperRecordRow, paper_id)
            if existing is None:
                row = PaperRecordRow(
                    paper_id=paper_id,
                    user_id=user_id,
                    source_name=source_name,
                    source_paper_id=source_paper_id,
                    title=title,
                    abstract=abstract,
                    authors_json=authors,
                    categories_json=categories,
                    discovered_watch_ids_json=[watch_id],
                    matched_query_terms_json=matched_query_terms,
                    published_at=published_at,
                    source_updated_at=source_updated_at,
                    source_abs_url=source_abs_url,
                    source_pdf_url=source_pdf_url,
                    pdf_status=pdf_status,
                    pdf_relative_path=pdf_relative_path,
                    pdf_error=pdf_error,
                    raw_source_json=raw_source,
                )
                session.add(row)
                await session.commit()
                await session.refresh(row)
                return PaperRecordUpsertResult(created=True, record=self._row_to_dict(row))

            changed = False
            changed |= self._set_if_changed(existing, "title", title)
            changed |= self._set_if_changed(existing, "abstract", abstract)
            changed |= self._set_if_changed(existing, "authors_json", authors)
            changed |= self._set_if_changed(existing, "categories_json", categories)
            changed |= self._set_if_changed(existing, "published_at", published_at)
            changed |= self._set_if_changed(existing, "source_updated_at", source_updated_at)
            changed |= self._set_if_changed(existing, "source_abs_url", source_abs_url)
            changed |= self._set_if_changed(existing, "source_pdf_url", source_pdf_url)
            changed |= self._set_if_changed(existing, "raw_source_json", raw_source)

            merged_watch_ids = self._merge_unique_strings(
                list(existing.discovered_watch_ids_json or []),
                [watch_id],
            )
            changed |= self._set_if_changed(existing, "discovered_watch_ids_json", merged_watch_ids)

            merged_query_terms = self._merge_unique_strings(
                list(existing.matched_query_terms_json or []),
                matched_query_terms,
            )
            changed |= self._set_if_changed(existing, "matched_query_terms_json", merged_query_terms)

            # 只在拿到更强的 PDF 事实时更新本地 PDF 状态，避免把 stored 降级成失败。
            if pdf_status == "stored" or existing.pdf_status != "stored":
                changed |= self._set_if_changed(existing, "pdf_status", pdf_status)
                changed |= self._set_if_changed(existing, "pdf_relative_path", pdf_relative_path)
                changed |= self._set_if_changed(existing, "pdf_error", pdf_error)

            if changed:
                await session.commit()
                await session.refresh(existing)

            return PaperRecordUpsertResult(created=False, record=self._row_to_dict(existing))

    async def list_papers(self, *, user_id: str, watch_id: str | None = None) -> list[dict[str, Any]]:
        """按最近更新时间倒序列出当前用户的 Paper Record。"""
        stmt = (
            select(PaperRecordRow)
            .where(PaperRecordRow.user_id == user_id)
            .order_by(
                PaperRecordRow.updated_at.desc(),
                PaperRecordRow.paper_id.desc(),
            )
        )
        async with self._sf() as session:
            result = await session.execute(stmt)
            rows = list(result.scalars())
        if watch_id is not None:
            rows = [row for row in rows if watch_id in (row.discovered_watch_ids_json or [])]
        return [self._row_to_dict(row) for row in rows]

    async def get_paper(self, paper_id: str, *, user_id: str) -> dict[str, Any] | None:
        """读取当前用户可见的单个 Paper Record 详情。"""
        async with self._sf() as session:
            row = await session.get(PaperRecordRow, paper_id)
            if row is None or row.user_id != user_id:
                return None
            return self._row_to_dict(row)
