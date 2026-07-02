"""Paper Record / Corpus 的浏览器 API。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from deerflow.persistence.engine import get_session_factory
from deerflow.persistence.paper_record import PaperRecordRepository

router = APIRouter(prefix="/api/papers", tags=["papers"])


def _get_user_id(request: Request) -> str:
    """从认证上下文读取当前用户。"""
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return str(user.id)


def _get_repository(request: Request) -> PaperRecordRepository:
    """优先复用 app.state 上的仓储，没有则按 session factory 构建。"""
    repo = getattr(request.app.state, "paper_record_repo", None)
    if isinstance(repo, PaperRecordRepository):
        return repo

    session_factory = get_session_factory()
    if session_factory is None:
        raise HTTPException(status_code=503, detail="Paper Record persistence is not available")

    repo = PaperRecordRepository(session_factory)
    request.app.state.paper_record_repo = repo
    return repo


class PaperRecordResponse(BaseModel):
    """单个 Paper Record 的 API 响应。"""

    paper_id: str
    source_name: str
    source_paper_id: str
    title: str
    abstract: str
    authors: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    discovered_watch_ids: list[str] = Field(default_factory=list)
    matched_query_terms: list[str] = Field(default_factory=list)
    published_at: str | None = None
    source_updated_at: str | None = None
    source_abs_url: str
    source_pdf_url: str | None = None
    pdf_status: str
    pdf_relative_path: str | None = None
    pdf_error: str | None = None
    created_at: str
    updated_at: str


class PaperRecordListResponse(BaseModel):
    """Paper Record 列表响应。"""

    papers: list[PaperRecordResponse] = Field(default_factory=list)


@router.get("", response_model=PaperRecordListResponse)
async def list_papers(
    request: Request,
    watch_id: str | None = Query(default=None),
) -> PaperRecordListResponse:
    """列出当前用户可见的 Paper Record，可选按 watch 过滤。"""
    repo = _get_repository(request)
    papers = await repo.list_papers(
        user_id=_get_user_id(request),
        watch_id=watch_id,
    )
    return PaperRecordListResponse(
        papers=[PaperRecordResponse.model_validate(item) for item in papers],
    )


@router.get("/{paper_id}", response_model=PaperRecordResponse)
async def get_paper(paper_id: str, request: Request) -> PaperRecordResponse:
    """读取当前用户的单个 Paper Record 详情。"""
    repo = _get_repository(request)
    paper = await repo.get_paper(paper_id, user_id=_get_user_id(request))
    if paper is None:
        raise HTTPException(status_code=404, detail=f"Paper Record '{paper_id}' not found")
    return PaperRecordResponse.model_validate(paper)
