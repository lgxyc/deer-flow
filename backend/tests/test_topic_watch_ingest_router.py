"""Topic Watch 手动 ingest 与 Paper Record 路由的外部行为测试。"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

import anyio
from _router_auth_helpers import make_authed_test_app
from fastapi.testclient import TestClient

from app.gateway.auth.models import User
from app.gateway.routers import paper_records, topic_watches


class _FakeArxivClient:
    """返回固定 arXiv 命中结果，避免测试依赖外网。"""

    def __init__(self, responses: dict[str, list[dict[str, object]]]) -> None:
        self._responses = responses
        self.calls: list[str] = []

    async def search(self, *, query: str, max_results: int) -> list[dict[str, object]]:
        self.calls.append(query)
        return list(self._responses.get(query, []))[:max_results]


async def _make_repos(tmp_path: Path):
    """初始化 Topic Watch / Paper Record 的测试仓储。"""
    from deerflow.persistence.engine import get_session_factory, init_engine
    from deerflow.persistence.paper_record import PaperRecordRepository
    from deerflow.persistence.topic_watch import TopicWatchRepository

    await init_engine(
        "sqlite",
        url=f"sqlite+aiosqlite:///{tmp_path / 'research-platform.db'}",
        sqlite_dir=str(tmp_path),
    )
    session_factory = get_session_factory()
    assert session_factory is not None
    return TopicWatchRepository(session_factory), PaperRecordRepository(session_factory)


def _user() -> User:
    """为测试应用提供稳定用户，避免 owner 维度漂移。"""
    return User(
        id=UUID("11111111-2222-3333-4444-555555555555"),
        email="research-platform@example.com",
        password_hash="x",
        system_role="user",
    )


def _make_app(*, watch_repo, paper_repo, ingest_service):
    """构造带鉴权桩、Topic Watch、Paper Record 与 ingest 服务的测试应用。"""
    app = make_authed_test_app(user_factory=_user)
    app.state.topic_watch_repo = watch_repo
    app.state.paper_record_repo = paper_repo
    app.state.topic_watch_ingest_service = ingest_service
    app.include_router(topic_watches.router)
    app.include_router(paper_records.router)
    return app


def _reset_paths(monkeypatch, tmp_path: Path) -> None:
    """把 DeerFlow 本地状态根目录重定向到测试临时目录。"""
    monkeypatch.setenv("DEER_FLOW_HOME", str(tmp_path / ".deer-flow"))
    import deerflow.config.paths as paths_mod

    monkeypatch.setattr(paths_mod, "_paths", None)


def test_manual_ingest_creates_paper_record_and_pdf_once(tmp_path: Path, monkeypatch) -> None:
    """成功路径：手动 ingest 会写入单个 Paper Record，并避免重复 PDF 下载。"""
    from deerflow.research.arxiv import ArxivPaperHit
    from deerflow.research.ingest import TopicWatchIngestService
    from deerflow.research.storage import ResearchPdfStore

    _reset_paths(monkeypatch, tmp_path)

    watch_repo, paper_repo = anyio.run(_make_repos, tmp_path)
    client = _FakeArxivClient(
        {
            "secure storage": [
                ArxivPaperHit(
                    source_paper_id="2501.00001",
                    title="Secure Storage with Deduplication",
                    abstract="This work studies secure storage and deduplication.",
                    authors=["Alice", "Bob"],
                    categories=["cs.CR"],
                    published_at="2025-01-01",
                    updated_at="2025-01-02",
                    abs_url="https://arxiv.org/abs/2501.00001",
                    pdf_url="https://arxiv.org/pdf/2501.00001.pdf",
                ).to_dict(),
                ArxivPaperHit(
                    source_paper_id="2501.99999",
                    title="An Unrelated Systems Paper",
                    abstract="This work studies distributed caches.",
                    authors=["Mallory"],
                    categories=["cs.DC"],
                    published_at="2025-01-03",
                    updated_at="2025-01-04",
                    abs_url="https://arxiv.org/abs/2501.99999",
                    pdf_url="https://arxiv.org/pdf/2501.99999.pdf",
                ).to_dict(),
            ],
            "deduplication": [
                ArxivPaperHit(
                    source_paper_id="2501.00001",
                    title="Secure Storage with Deduplication",
                    abstract="This work studies secure storage and deduplication.",
                    authors=["Alice", "Bob"],
                    categories=["cs.CR"],
                    published_at="2025-01-01",
                    updated_at="2025-01-02",
                    abs_url="https://arxiv.org/abs/2501.00001",
                    pdf_url="https://arxiv.org/pdf/2501.00001.pdf",
                ).to_dict(),
            ],
        },
    )
    download_calls: list[str] = []

    async def _download_pdf(url: str) -> bytes:
        download_calls.append(url)
        return b"%PDF-1.4 fake"

    ingest_service = TopicWatchIngestService(
        topic_watch_repo=watch_repo,
        paper_record_repo=paper_repo,
        arxiv_client=client,
        pdf_store=ResearchPdfStore(download_pdf=_download_pdf),
    )
    app = _make_app(watch_repo=watch_repo, paper_repo=paper_repo, ingest_service=ingest_service)

    with TestClient(app) as test_client:
        created_watch = test_client.post(
            "/api/topic-watches",
            json={
                "watch_id": "watch-security-storage",
                "query_terms": ["secure storage", "deduplication"],
                "seed_papers": [],
                "template_family": "solution_platform",
                "schedule_preset": "weekly",
                "enabled": True,
            },
        )
        assert created_watch.status_code == 200, created_watch.text

        first_run = test_client.post("/api/topic-watches/watch-security-storage/ingest")
        second_run = test_client.post("/api/topic-watches/watch-security-storage/ingest")
        listed = test_client.get("/api/papers")

    assert first_run.status_code == 200, first_run.text
    assert first_run.json()["watch_id"] == "watch-security-storage"
    assert first_run.json()["total_hits"] == 3
    assert first_run.json()["screened_in_count"] == 1
    assert first_run.json()["created_count"] == 1
    assert first_run.json()["deduped_count"] == 0
    assert first_run.json()["failed_count"] == 0
    assert len(first_run.json()["papers"]) == 1

    paper = first_run.json()["papers"][0]
    assert paper["source_name"] == "arxiv"
    assert paper["source_paper_id"] == "2501.00001"
    assert paper["pdf_status"] == "stored"
    assert paper["matched_query_terms"] == ["secure storage", "deduplication"]
    assert paper["discovered_watch_ids"] == ["watch-security-storage"]

    assert second_run.status_code == 200, second_run.text
    assert second_run.json()["created_count"] == 0
    assert second_run.json()["deduped_count"] == 1
    assert len(listed.json()["papers"]) == 1
    assert download_calls == ["https://arxiv.org/pdf/2501.00001.pdf"]

    paper_id = paper["paper_id"]
    with TestClient(app) as test_client:
        detail = test_client.get(f"/api/papers/{paper_id}")

    assert detail.status_code == 200, detail.text
    assert detail.json()["paper_id"] == paper_id
    assert detail.json()["pdf_status"] == "stored"

    from deerflow.config.paths import get_paths

    relative_pdf_path = Path(detail.json()["pdf_relative_path"])
    stored_pdf = get_paths().user_dir(str(_user().id)) / relative_pdf_path
    assert stored_pdf.exists(), "ingest 应该把 PDF 落到 DeerFlow 本地 corpus 路径"


def test_manual_ingest_keeps_paper_records_user_scoped(tmp_path: Path, monkeypatch) -> None:
    """相同 arXiv 论文被不同用户 ingest 时，应各自拥有独立的 Paper Record。"""
    from deerflow.research.arxiv import ArxivPaperHit
    from deerflow.research.ingest import TopicWatchIngestService
    from deerflow.research.storage import ResearchPdfStore

    _reset_paths(monkeypatch, tmp_path)

    watch_repo, paper_repo = anyio.run(_make_repos, tmp_path)
    client = _FakeArxivClient(
        {
            "secure storage": [
                ArxivPaperHit(
                    source_paper_id="2501.00003",
                    title="Secure Storage for Two Users",
                    abstract="secure storage result",
                    authors=["Alice"],
                    categories=["cs.CR"],
                    published_at="2025-02-01",
                    updated_at="2025-02-02",
                    abs_url="https://arxiv.org/abs/2501.00003",
                    pdf_url="https://arxiv.org/pdf/2501.00003.pdf",
                ).to_dict(),
            ],
        },
    )

    async def _download_pdf(_url: str) -> bytes:
        return b"%PDF-1.4 fake"

    ingest_service = TopicWatchIngestService(
        topic_watch_repo=watch_repo,
        paper_record_repo=paper_repo,
        arxiv_client=client,
        pdf_store=ResearchPdfStore(download_pdf=_download_pdf),
    )

    primary_app = _make_app(
        watch_repo=watch_repo,
        paper_repo=paper_repo,
        ingest_service=ingest_service,
    )
    secondary_app = make_authed_test_app(
        user_factory=lambda: User(
            id=UUID("99999999-2222-3333-4444-555555555555"),
            email="second-user@example.com",
            password_hash="x",
            system_role="user",
        ),
    )
    secondary_app.state.topic_watch_repo = watch_repo
    secondary_app.state.paper_record_repo = paper_repo
    secondary_app.state.topic_watch_ingest_service = ingest_service
    secondary_app.include_router(topic_watches.router)
    secondary_app.include_router(paper_records.router)

    with TestClient(primary_app) as primary_client:
        created_primary_watch = primary_client.post(
            "/api/topic-watches",
            json={
                "watch_id": "watch-user-a",
                "query_terms": ["secure storage"],
                "seed_papers": [],
                "template_family": "solution_platform",
                "schedule_preset": "weekly",
                "enabled": True,
            },
        )
        assert created_primary_watch.status_code == 200, created_primary_watch.text
        first_run = primary_client.post("/api/topic-watches/watch-user-a/ingest")
        first_list = primary_client.get("/api/papers")

    with TestClient(secondary_app) as secondary_client:
        created_secondary_watch = secondary_client.post(
            "/api/topic-watches",
            json={
                "watch_id": "watch-user-b",
                "query_terms": ["secure storage"],
                "seed_papers": [],
                "template_family": "solution_platform",
                "schedule_preset": "weekly",
                "enabled": True,
            },
        )
        assert created_secondary_watch.status_code == 200, created_secondary_watch.text
        second_run = secondary_client.post("/api/topic-watches/watch-user-b/ingest")
        second_list = secondary_client.get("/api/papers")

    assert first_run.status_code == 200, first_run.text
    assert second_run.status_code == 200, second_run.text
    assert first_run.json()["created_count"] == 1
    assert second_run.json()["created_count"] == 1
    assert len(first_list.json()["papers"]) == 1
    assert len(second_list.json()["papers"]) == 1
    assert first_list.json()["papers"][0]["paper_id"] != second_list.json()["papers"][0]["paper_id"]


def test_manual_ingest_surfaces_pdf_download_failure_status(tmp_path: Path, monkeypatch) -> None:
    """失败路径：PDF 下载失败时，Paper Record 仍应保留失败状态。"""
    from deerflow.research.arxiv import ArxivPaperHit
    from deerflow.research.ingest import TopicWatchIngestService
    from deerflow.research.storage import ResearchPdfStore

    _reset_paths(monkeypatch, tmp_path)

    watch_repo, paper_repo = anyio.run(_make_repos, tmp_path)
    client = _FakeArxivClient(
        {
            "secure storage": [
                ArxivPaperHit(
                    source_paper_id="2501.00002",
                    title="A Failed PDF Example",
                    abstract="This work studies secure storage.",
                    authors=["Alice"],
                    categories=["cs.CR"],
                    published_at="2025-02-01",
                    updated_at="2025-02-02",
                    abs_url="https://arxiv.org/abs/2501.00002",
                    pdf_url="https://arxiv.org/pdf/2501.00002.pdf",
                ).to_dict(),
            ],
        },
    )

    async def _download_pdf(_url: str) -> bytes:
        raise RuntimeError("upstream pdf download failed")

    ingest_service = TopicWatchIngestService(
        topic_watch_repo=watch_repo,
        paper_record_repo=paper_repo,
        arxiv_client=client,
        pdf_store=ResearchPdfStore(download_pdf=_download_pdf),
    )
    app = _make_app(watch_repo=watch_repo, paper_repo=paper_repo, ingest_service=ingest_service)

    with TestClient(app) as test_client:
        created_watch = test_client.post(
            "/api/topic-watches",
            json={
                "watch_id": "watch-failure",
                "query_terms": ["secure storage"],
                "seed_papers": [],
                "template_family": "solution_platform",
                "schedule_preset": "weekly",
                "enabled": True,
            },
        )
        assert created_watch.status_code == 200, created_watch.text

        response = test_client.post("/api/topic-watches/watch-failure/ingest")
        listed = test_client.get("/api/papers")

    assert response.status_code == 200, response.text
    assert response.json()["created_count"] == 1
    assert response.json()["failed_count"] == 1
    assert response.json()["papers"][0]["pdf_status"] == "download_failed"
    assert response.json()["papers"][0]["pdf_relative_path"] is None

    assert listed.status_code == 200, listed.text
    assert listed.json()["papers"][0]["pdf_status"] == "download_failed"
