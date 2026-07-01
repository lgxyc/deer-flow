"""Topic Watch 的 SQLAlchemy 仓储实现。"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deerflow.persistence.topic_watch.model import TopicWatchRow
from deerflow.utils.time import coerce_iso


class TopicWatchConflictError(RuntimeError):
    """同一个 watch_id 被不同请求语义复用时抛出。"""


class TopicWatchRepository:
    """提供 Topic Watch 的 create/list/get 访问面。"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    @staticmethod
    def _new_watch_id() -> str:
        """生成服务端兜底的 watch_id。"""
        return uuid4().hex

    @staticmethod
    def _coerce_datetime(value: datetime) -> str:
        """把 SQLite 可能丢失时区的时间戳统一转成 ISO 字符串。"""
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return coerce_iso(value)

    @classmethod
    def _row_to_dict(cls, row: TopicWatchRow) -> dict[str, Any]:
        """把 ORM 行对象转换成 API 友好的扁平字典。"""
        data = row.to_dict()
        data["query_terms"] = data.pop("query_terms_json") or []
        data["seed_papers"] = data.pop("seed_papers_json") or []
        data["created_at"] = cls._coerce_datetime(row.created_at)
        data["updated_at"] = cls._coerce_datetime(row.updated_at)
        return data

    @staticmethod
    def _matches_existing(
        row: TopicWatchRow,
        *,
        user_id: str,
        query_terms: list[str],
        seed_papers: list[str],
        template_family: str,
        schedule_preset: str,
        enabled: bool,
    ) -> bool:
        """判断重复 create 是否真的是同一份请求重试。"""
        return (
            row.user_id == user_id
            and list(row.query_terms_json or []) == query_terms
            and list(row.seed_papers_json or []) == seed_papers
            and row.template_family == template_family
            and row.schedule_preset == schedule_preset
            and row.enabled == enabled
        )

    async def create_watch(
        self,
        *,
        user_id: str,
        watch_id: str | None,
        query_terms: list[str],
        seed_papers: list[str],
        template_family: str,
        schedule_preset: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """创建 Topic Watch，并支持同一 ``watch_id`` 的幂等重试。"""
        resolved_watch_id = watch_id or self._new_watch_id()
        async with self._sf() as session:
            existing = await session.get(TopicWatchRow, resolved_watch_id)
            if existing is not None:
                if self._matches_existing(
                    existing,
                    user_id=user_id,
                    query_terms=query_terms,
                    seed_papers=seed_papers,
                    template_family=template_family,
                    schedule_preset=schedule_preset,
                    enabled=enabled,
                ):
                    return self._row_to_dict(existing)
                raise TopicWatchConflictError(
                    f"watch_id '{resolved_watch_id}' is already used by a different Topic Watch request",
                )

            row = TopicWatchRow(
                watch_id=resolved_watch_id,
                user_id=user_id,
                query_terms_json=query_terms,
                seed_papers_json=seed_papers,
                template_family=template_family,
                schedule_preset=schedule_preset,
                enabled=enabled,
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)
            return self._row_to_dict(row)

    async def list_watches(self, *, user_id: str) -> list[dict[str, Any]]:
        """按最近更新时间倒序列出当前用户的 Topic Watch。"""
        stmt = select(TopicWatchRow).where(TopicWatchRow.user_id == user_id).order_by(TopicWatchRow.updated_at.desc(), TopicWatchRow.watch_id.desc())
        async with self._sf() as session:
            result = await session.execute(stmt)
            return [self._row_to_dict(row) for row in result.scalars()]

    async def get_watch(self, watch_id: str, *, user_id: str) -> dict[str, Any] | None:
        """读取当前用户可见的单个 Topic Watch。"""
        async with self._sf() as session:
            row = await session.get(TopicWatchRow, watch_id)
            if row is None or row.user_id != user_id:
                return None
            return self._row_to_dict(row)
