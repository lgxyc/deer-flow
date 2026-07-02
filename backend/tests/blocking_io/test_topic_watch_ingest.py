"""回归锚点：Topic Watch ingest 必须把 corpus PDF 文件写入下放到线程。

手动 ingest 会为通过初筛的论文创建 corpus 目录并写入 PDF。这个路径处在
FastAPI 的异步请求链上，因此任何 ``mkdir`` / ``write_bytes`` / ``exists``
之类的阻塞文件 I/O 都必须显式下放到 ``asyncio.to_thread``。如果后续有人把
这些操作重新搬回事件循环，本测试会在严格 Blockbuster gate 下失败。
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from deerflow.research.arxiv import ArxivPaperHit
from deerflow.research.ingest import TopicWatchIngestService
from deerflow.research.storage import ResearchPdfStore

pytestmark = pytest.mark.asyncio


class _FakeArxivClient:
    """为 blocking-io 锚点提供纯内存搜索结果。"""

    async def search(self, *, query: str, max_results: int) -> list[dict[str, object]]:
        """始终返回一条固定命中，把门禁焦点收缩到本地文件写入。"""
        del query, max_results
        return [
            ArxivPaperHit(
                source_paper_id="2501.00003",
                title="Secure Storage for Blocking-IO Test",
                abstract="A paper used to guard corpus pdf writes.",
                authors=["Alice"],
                categories=["cs.CR"],
                published_at="2025-03-01",
                updated_at="2025-03-02",
                abs_url="https://arxiv.org/abs/2501.00003",
                pdf_url="https://arxiv.org/pdf/2501.00003.pdf",
            ).to_dict(),
        ]


class _FakeTopicWatchRepository:
    """只提供 ingest 需要的 Topic Watch 读取面。"""

    async def get_watch(self, watch_id: str, *, user_id: str) -> dict[str, object] | None:
        """返回单个固定 watch，避免测试引入额外持久化噪音。"""
        if watch_id != "watch-blocking-io" or user_id != "u1":
            return None
        return {
            "watch_id": watch_id,
            "query_terms": ["secure storage"],
            "seed_papers": [],
        }


class _FakePaperRecordRepository:
    """只提供 ingest 需要的 Paper Record upsert 面。"""

    async def upsert_paper(self, **kwargs) -> object:
        """返回最小 upsert 结果，让测试只观察 PDF 落盘路径。"""
        return type(
            "_UpsertResult",
            (),
            {
                "created": True,
                "record": {
                    "paper_id": "paper-1",
                    "source_name": kwargs["source_name"],
                    "source_paper_id": kwargs["source_paper_id"],
                    "title": kwargs["title"],
                    "abstract": kwargs["abstract"],
                    "authors": kwargs["authors"],
                    "categories": kwargs["categories"],
                    "discovered_watch_ids": [kwargs["watch_id"]],
                    "matched_query_terms": kwargs["matched_query_terms"],
                    "published_at": kwargs["published_at"],
                    "source_updated_at": kwargs["source_updated_at"],
                    "source_abs_url": kwargs["source_abs_url"],
                    "source_pdf_url": kwargs["source_pdf_url"],
                    "pdf_status": kwargs["pdf_status"],
                    "pdf_relative_path": kwargs["pdf_relative_path"],
                    "pdf_error": kwargs["pdf_error"],
                    "created_at": "2026-07-01T00:00:00Z",
                    "updated_at": "2026-07-01T00:00:00Z",
                },
            },
        )()


async def test_topic_watch_ingest_does_not_block_event_loop(tmp_path: Path, monkeypatch) -> None:
    """手动 ingest 的本地 PDF 路径必须完全避开事件循环阻塞 I/O。"""
    monkeypatch.setenv("DEER_FLOW_HOME", str(tmp_path / ".deer-flow"))
    import deerflow.config.paths as paths_mod

    monkeypatch.setattr(paths_mod, "_paths", None)

    async def _download_pdf(_url: str) -> bytes:
        return b"%PDF-1.4 fake"

    service = TopicWatchIngestService(
        topic_watch_repo=_FakeTopicWatchRepository(),
        paper_record_repo=_FakePaperRecordRepository(),
        arxiv_client=_FakeArxivClient(),
        pdf_store=ResearchPdfStore(download_pdf=_download_pdf),
    )

    result = await service.run_manual_ingest(user_id="u1", watch_id="watch-blocking-io")

    assert result.created_count == 1
    relative_pdf_path = Path(result.papers[0]["pdf_relative_path"])
    stored_pdf = tmp_path / ".deer-flow" / "users" / "u1" / relative_pdf_path
    exists = await asyncio.to_thread(stored_pdf.exists)
    assert exists, "ingest 应该把 PDF 写到 tmp corpus 路径"
