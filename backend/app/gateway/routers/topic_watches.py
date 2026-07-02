"""Topic Watch 的浏览器 API。"""

from __future__ import annotations

from typing import ClassVar

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from app.gateway.routers.paper_records import PaperRecordResponse
from deerflow.persistence.engine import get_session_factory
from deerflow.persistence.paper_record import PaperRecordRepository
from deerflow.persistence.topic_watch import TopicWatchConflictError, TopicWatchRepository
from deerflow.research.ingest import (
    TopicWatchIngestError,
    TopicWatchIngestService,
    TopicWatchNotFoundError,
)

router = APIRouter(prefix="/api/topic-watches", tags=["topic-watches"])


def _get_user_id(request: Request) -> str:
    """从认证上下文读取当前用户。"""
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return str(user.id)


def _get_repository(request: Request) -> TopicWatchRepository:
    """优先复用 app.state 上的仓储，没有则按 session factory 构建。"""
    repo = getattr(request.app.state, "topic_watch_repo", None)
    if isinstance(repo, TopicWatchRepository):
        return repo

    session_factory = get_session_factory()
    if session_factory is None:
        raise HTTPException(status_code=503, detail="Topic Watch persistence is not available")

    repo = TopicWatchRepository(session_factory)
    request.app.state.topic_watch_repo = repo
    return repo


def _get_paper_record_repository(request: Request) -> PaperRecordRepository:
    """优先复用 app.state 上的 Paper Record 仓储。"""
    repo = getattr(request.app.state, "paper_record_repo", None)
    if isinstance(repo, PaperRecordRepository):
        return repo

    session_factory = get_session_factory()
    if session_factory is None:
        raise HTTPException(status_code=503, detail="Paper Record persistence is not available")

    repo = PaperRecordRepository(session_factory)
    request.app.state.paper_record_repo = repo
    return repo


def _get_ingest_service(request: Request) -> TopicWatchIngestService:
    """优先复用 app.state 上的 ingest 服务，没有则按 repo 组装。"""
    service = getattr(request.app.state, "topic_watch_ingest_service", None)
    if isinstance(service, TopicWatchIngestService):
        return service

    service = TopicWatchIngestService(
        topic_watch_repo=_get_repository(request),
        paper_record_repo=_get_paper_record_repository(request),
    )
    request.app.state.topic_watch_ingest_service = service
    return service


class TopicWatchResponse(BaseModel):
    """单个 Topic Watch 的 API 响应。"""

    watch_id: str
    query_terms: list[str] = Field(default_factory=list)
    seed_papers: list[str] = Field(default_factory=list)
    template_family: str
    schedule_preset: str
    enabled: bool
    created_at: str
    updated_at: str


class TopicWatchListResponse(BaseModel):
    """Topic Watch 列表响应。"""

    watches: list[TopicWatchResponse] = Field(default_factory=list)


class TopicWatchCreateRequest(BaseModel):
    """创建 Topic Watch 的请求体。"""

    _VALID_TEMPLATE_FAMILIES: ClassVar[tuple[str, ...]] = (
        "solution_platform",
        "survey",
    )
    _VALID_SCHEDULE_PRESETS: ClassVar[tuple[str, ...]] = (
        "daily",
        "every_3_days",
        "weekly",
    )

    watch_id: str | None = Field(default=None, description="客户端幂等 key，可选")
    query_terms: list[str] = Field(default_factory=list)
    seed_papers: list[str] = Field(default_factory=list)
    template_family: str
    schedule_preset: str
    enabled: bool = True

    @field_validator("watch_id")
    @classmethod
    def _validate_watch_id(cls, value: str | None) -> str | None:
        """限制 watch_id 为空或可读字符串，避免把空白串写入主键。"""
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("watch_id must not be empty when provided")
        return normalized

    @field_validator("query_terms", "seed_papers")
    @classmethod
    def _normalize_string_list(cls, value: list[str]) -> list[str]:
        """去掉空白项并按出现顺序去重，避免 UI 文本框带入脏值。"""
        normalized: list[str] = []
        seen: set[str] = set()
        for item in value:
            cleaned = item.strip()
            if not cleaned or cleaned in seen:
                continue
            normalized.append(cleaned)
            seen.add(cleaned)
        return normalized

    @field_validator("query_terms")
    @classmethod
    def _require_query_terms(cls, value: list[str]) -> list[str]:
        """至少保留一个 query term，保证 Topic Watch 有明确查询意图。"""
        if not value:
            raise ValueError("query_terms must contain at least one non-empty entry")
        return value

    @field_validator("template_family")
    @classmethod
    def _validate_template_family(cls, value: str) -> str:
        """只允许显式支持的模板族，保持控制平面稳定。"""
        if value not in cls._VALID_TEMPLATE_FAMILIES:
            expected = ", ".join(cls._VALID_TEMPLATE_FAMILIES)
            raise ValueError(f"template_family must be one of: {expected}")
        return value

    @field_validator("schedule_preset")
    @classmethod
    def _validate_schedule_preset(cls, value: str) -> str:
        """只允许固定调度预设，拒绝任意 cron 风格值。"""
        if value not in cls._VALID_SCHEDULE_PRESETS:
            expected = ", ".join(cls._VALID_SCHEDULE_PRESETS)
            raise ValueError(f"schedule_preset must be one of: {expected}")
        return value


class TopicWatchIngestResponse(BaseModel):
    """一次手动 ingest 的聚合响应。"""

    watch_id: str
    searched_queries: list[str] = Field(default_factory=list)
    total_hits: int
    screened_in_count: int
    created_count: int
    deduped_count: int
    failed_count: int
    papers: list[PaperRecordResponse] = Field(default_factory=list)


@router.post("", response_model=TopicWatchResponse)
async def create_topic_watch(
    body: TopicWatchCreateRequest,
    request: Request,
) -> TopicWatchResponse:
    """创建 Topic Watch，并在同一 ``watch_id`` 上保持幂等。"""
    repo = _get_repository(request)
    try:
        watch = await repo.create_watch(
            user_id=_get_user_id(request),
            watch_id=body.watch_id,
            query_terms=body.query_terms,
            seed_papers=body.seed_papers,
            template_family=body.template_family,
            schedule_preset=body.schedule_preset,
            enabled=body.enabled,
        )
    except TopicWatchConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return TopicWatchResponse.model_validate(watch)


@router.get("", response_model=TopicWatchListResponse)
async def list_topic_watches(request: Request) -> TopicWatchListResponse:
    """列出当前用户的 Topic Watch。"""
    repo = _get_repository(request)
    watches = await repo.list_watches(user_id=_get_user_id(request))
    return TopicWatchListResponse(
        watches=[TopicWatchResponse.model_validate(item) for item in watches],
    )


@router.get("/{watch_id}", response_model=TopicWatchResponse)
async def get_topic_watch(watch_id: str, request: Request) -> TopicWatchResponse:
    """读取当前用户的 Topic Watch 详情。"""
    repo = _get_repository(request)
    watch = await repo.get_watch(watch_id, user_id=_get_user_id(request))
    if watch is None:
        raise HTTPException(status_code=404, detail=f"Topic Watch '{watch_id}' not found")
    return TopicWatchResponse.model_validate(watch)


@router.post("/{watch_id}/ingest", response_model=TopicWatchIngestResponse)
async def run_topic_watch_ingest(watch_id: str, request: Request) -> TopicWatchIngestResponse:
    """从指定 Topic Watch 触发一次手动 arXiv ingest。"""
    service = _get_ingest_service(request)
    try:
        result = await service.run_manual_ingest(
            user_id=_get_user_id(request),
            watch_id=watch_id,
        )
    except TopicWatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TopicWatchIngestError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return TopicWatchIngestResponse(
        watch_id=result.watch_id,
        searched_queries=result.searched_queries,
        total_hits=result.total_hits,
        screened_in_count=result.screened_in_count,
        created_count=result.created_count,
        deduped_count=result.deduped_count,
        failed_count=result.failed_count,
        papers=[PaperRecordResponse.model_validate(item) for item in result.papers],
    )
