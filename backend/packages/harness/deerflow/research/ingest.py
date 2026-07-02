"""Topic Watch 手动 ingest 深模块。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from deerflow.persistence.paper_record import PaperRecordRepository
from deerflow.persistence.topic_watch import TopicWatchRepository
from deerflow.research.arxiv import ArxivClient, ArxivPaperHit, ArxivQueryError
from deerflow.research.storage import ResearchPdfStore

DEFAULT_MAX_RESULTS_PER_QUERY = 5


class ArxivSearchClient(Protocol):
    """Topic Watch ingest 依赖的最小 arXiv 搜索面。"""

    async def search(self, *, query: str, max_results: int) -> list[dict[str, object]]:
        """按 query 拉取结构化 arXiv 命中。"""


class PdfStore(Protocol):
    """Topic Watch ingest 依赖的最小 PDF 存储面。"""

    async def store_pdf(
        self,
        *,
        user_id: str,
        source_name: str,
        source_paper_id: str,
        pdf_url: str | None,
    ):
        """保存 PDF 并返回可序列化结果。"""


class TopicWatchIngestError(RuntimeError):
    """Topic Watch ingest 执行失败时抛出。"""


class TopicWatchNotFoundError(TopicWatchIngestError):
    """目标 Topic Watch 不存在时抛出。"""


@dataclass(slots=True, frozen=True)
class TopicWatchIngestResult:
    """一次手动 ingest 的聚合结果。"""

    watch_id: str
    searched_queries: list[str]
    total_hits: int
    screened_in_count: int
    created_count: int
    deduped_count: int
    failed_count: int
    papers: list[dict[str, Any]]


class TopicWatchIngestService:
    """把 Topic Watch 变成 Paper Record/PDF Corpus 的手动 ingest 服务。"""

    def __init__(
        self,
        *,
        topic_watch_repo: TopicWatchRepository,
        paper_record_repo: PaperRecordRepository,
        arxiv_client: ArxivSearchClient | None = None,
        pdf_store: PdfStore | None = None,
        max_results_per_query: int = DEFAULT_MAX_RESULTS_PER_QUERY,
    ) -> None:
        self._topic_watch_repo = topic_watch_repo
        self._paper_record_repo = paper_record_repo
        self._arxiv_client = arxiv_client or ArxivClient()
        self._pdf_store = pdf_store or ResearchPdfStore()
        self._max_results_per_query = max_results_per_query

    @staticmethod
    def _merge_unique_strings(existing: list[str], additions: list[str]) -> list[str]:
        """保留原顺序合并字符串列表。"""
        merged = list(existing)
        seen = set(existing)
        for item in additions:
            if not item or item in seen:
                continue
            merged.append(item)
            seen.add(item)
        return merged

    @staticmethod
    def _normalize_seed_paper_ids(seed_papers: list[str]) -> set[str]:
        """把 seed papers 归一到可与 arXiv source id 比较的形式。"""
        normalized: set[str] = set()
        for item in seed_papers:
            cleaned = item.strip()
            if cleaned.lower().startswith("arxiv:"):
                cleaned = cleaned.split(":", 1)[1]
            if cleaned:
                normalized.add(cleaned)
        return normalized

    @staticmethod
    def _screened_query_terms(
        candidate: dict[str, Any],
        *,
        query_terms: list[str],
    ) -> list[str]:
        """只保留真正出现在标题/摘要中的 query term，形成最小初筛。"""
        haystack = " ".join(
            [
                str(candidate.get("title") or ""),
                str(candidate.get("abstract") or ""),
            ],
        ).lower()
        screened_terms: list[str] = []
        for query in query_terms:
            normalized = query.strip().lower()
            if normalized and normalized in haystack:
                screened_terms.append(query)
        return screened_terms

    @staticmethod
    def _passes_initial_screening(
        candidate: dict[str, Any],
        *,
        seed_paper_ids: set[str],
    ) -> bool:
        """当前 slice 的初筛策略：标题/摘要命中 query term，或显式对上 seed paper。"""
        if candidate.get("screened_query_terms"):
            return True
        return str(candidate["source_paper_id"]) in seed_paper_ids

    async def _collect_candidates(self, query_terms: list[str]) -> tuple[int, list[dict[str, Any]]]:
        """按 query term 聚合 arXiv 命中，并在同一 run 内完成去重。"""
        total_hits = 0
        deduped_candidates: dict[str, dict[str, Any]] = {}

        for query in query_terms:
            try:
                hits = await self._arxiv_client.search(
                    query=query,
                    max_results=self._max_results_per_query,
                )
            except ArxivQueryError as exc:
                raise TopicWatchIngestError(str(exc)) from exc
            except Exception as exc:  # noqa: BLE001 - 需要把 adapter 异常变成可理解失败
                raise TopicWatchIngestError(f"manual ingest failed to query arXiv for '{query}': {exc}") from exc

            total_hits += len(hits)
            for raw_hit in hits:
                hit = ArxivPaperHit.from_dict(raw_hit)
                existing = deduped_candidates.get(hit.source_paper_id)
                if existing is None:
                    payload = hit.to_dict()
                    payload["matched_query_terms"] = [query]
                    deduped_candidates[hit.source_paper_id] = payload
                    continue
                existing["matched_query_terms"] = self._merge_unique_strings(
                    list(existing.get("matched_query_terms", [])),
                    [query],
                )

        return total_hits, list(deduped_candidates.values())

    async def run_manual_ingest(self, *, user_id: str, watch_id: str) -> TopicWatchIngestResult:
        """执行一次 Topic Watch -> Paper Record/PDF Corpus 的手动 ingest。"""
        watch = await self._topic_watch_repo.get_watch(watch_id, user_id=user_id)
        if watch is None:
            raise TopicWatchNotFoundError(f"Topic Watch '{watch_id}' not found")

        query_terms = [str(item) for item in watch.get("query_terms", [])]
        seed_paper_ids = self._normalize_seed_paper_ids([str(item) for item in watch.get("seed_papers", [])])
        total_hits, candidates = await self._collect_candidates(query_terms)
        for candidate in candidates:
            candidate["screened_query_terms"] = self._screened_query_terms(
                candidate,
                query_terms=query_terms,
            )
        screened_candidates = [
            candidate
            for candidate in candidates
            if self._passes_initial_screening(
                candidate,
                seed_paper_ids=seed_paper_ids,
            )
        ]

        papers: list[dict[str, Any]] = []
        created_count = 0
        deduped_count = 0
        failed_count = 0

        for candidate in screened_candidates:
            hit = ArxivPaperHit.from_dict(candidate)
            pdf_result = await self._pdf_store.store_pdf(
                user_id=user_id,
                source_name="arxiv",
                source_paper_id=hit.source_paper_id,
                pdf_url=hit.pdf_url,
            )
            upsert_result = await self._paper_record_repo.upsert_paper(
                user_id=user_id,
                watch_id=watch_id,
                source_name="arxiv",
                source_paper_id=hit.source_paper_id,
                title=hit.title,
                abstract=hit.abstract,
                authors=hit.authors,
                categories=hit.categories,
                matched_query_terms=list(candidate.get("screened_query_terms", [])),
                published_at=hit.published_at,
                source_updated_at=hit.updated_at,
                source_abs_url=hit.abs_url,
                source_pdf_url=hit.pdf_url,
                pdf_status=pdf_result.status,
                pdf_relative_path=pdf_result.relative_path,
                pdf_error=pdf_result.error,
                raw_source=hit.to_dict(),
            )
            if upsert_result.created:
                created_count += 1
            else:
                deduped_count += 1
            if pdf_result.status != "stored":
                failed_count += 1
            papers.append(upsert_result.record)

        return TopicWatchIngestResult(
            watch_id=watch_id,
            searched_queries=query_terms,
            total_hits=total_hits,
            screened_in_count=len(screened_candidates),
            created_count=created_count,
            deduped_count=deduped_count,
            failed_count=failed_count,
            papers=papers,
        )
