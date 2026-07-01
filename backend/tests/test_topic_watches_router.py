"""Topic Watch 路由的外部行为测试。"""

from __future__ import annotations

from uuid import UUID

import anyio
from _router_auth_helpers import make_authed_test_app
from fastapi.testclient import TestClient

from app.gateway.auth.models import User
from app.gateway.routers import topic_watches


async def _make_repo(tmp_path):
    from deerflow.persistence.engine import get_session_factory, init_engine
    from deerflow.persistence.topic_watch import TopicWatchRepository

    await init_engine(
        "sqlite",
        url=f"sqlite+aiosqlite:///{tmp_path / 'topic-watches.db'}",
        sqlite_dir=str(tmp_path),
    )
    session_factory = get_session_factory()
    assert session_factory is not None
    return TopicWatchRepository(session_factory)


def _make_app(repo):
    """构造带鉴权桩和 Topic Watch 仓储的测试应用。"""
    app = make_authed_test_app(user_factory=_user)
    app.state.topic_watch_repo = repo
    app.include_router(topic_watches.router)
    return app


def _user() -> User:
    """为整个测试进程提供稳定用户，避免每次请求 owner 漂移。"""
    return User(
        id=UUID("11111111-2222-3333-4444-555555555555"),
        email="topic-watch@example.com",
        password_hash="x",
        system_role="user",
    )


def test_create_list_and_get_topic_watch(tmp_path):
    repo = anyio.run(_make_repo, tmp_path)
    app = _make_app(repo)

    payload = {
        "watch_id": "watch-security-storage",
        "query_terms": ["secure storage", "  deduplication  ", "secure storage"],
        "seed_papers": ["arXiv:2501.00001", " ", "arXiv:2501.00001"],
        "template_family": "solution_platform",
        "schedule_preset": "weekly",
        "enabled": True,
    }

    with TestClient(app) as client:
        created = client.post("/api/topic-watches", json=payload)
        listed = client.get("/api/topic-watches")
        detail = client.get("/api/topic-watches/watch-security-storage")

    assert created.status_code == 200, created.text
    assert created.json()["watch_id"] == "watch-security-storage"
    assert created.json()["query_terms"] == ["secure storage", "deduplication"]
    assert created.json()["seed_papers"] == ["arXiv:2501.00001"]

    assert listed.status_code == 200, listed.text
    assert [item["watch_id"] for item in listed.json()["watches"]] == [
        "watch-security-storage",
    ]

    assert detail.status_code == 200, detail.text
    assert detail.json()["template_family"] == "solution_platform"
    assert detail.json()["schedule_preset"] == "weekly"


def test_create_topic_watch_is_idempotent_for_same_watch_id(tmp_path):
    repo = anyio.run(_make_repo, tmp_path)
    app = _make_app(repo)

    payload = {
        "watch_id": "watch-idempotent",
        "query_terms": ["secure storage"],
        "seed_papers": [],
        "template_family": "survey",
        "schedule_preset": "daily",
        "enabled": False,
    }

    with TestClient(app) as client:
        first = client.post("/api/topic-watches", json=payload)
        second = client.post("/api/topic-watches", json=payload)
        listed = client.get("/api/topic-watches")

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert first.json() == second.json()
    assert len(listed.json()["watches"]) == 1


def test_invalid_template_family_is_rejected(tmp_path):
    repo = anyio.run(_make_repo, tmp_path)
    app = _make_app(repo)

    with TestClient(app) as client:
        response = client.post(
            "/api/topic-watches",
            json={
                "query_terms": ["secure storage"],
                "seed_papers": [],
                "template_family": "unknown_template",
                "schedule_preset": "daily",
                "enabled": True,
            },
        )

    assert response.status_code == 422
    assert "template_family must be one of" in response.text


def test_invalid_schedule_preset_is_rejected(tmp_path):
    repo = anyio.run(_make_repo, tmp_path)
    app = _make_app(repo)

    with TestClient(app) as client:
        response = client.post(
            "/api/topic-watches",
            json={
                "query_terms": ["secure storage"],
                "seed_papers": [],
                "template_family": "solution_platform",
                "schedule_preset": "hourly",
                "enabled": True,
            },
        )

    assert response.status_code == 422
    assert "schedule_preset must be one of" in response.text
