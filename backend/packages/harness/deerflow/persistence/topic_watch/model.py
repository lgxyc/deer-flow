"""Topic Watch ORM 模型。"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from deerflow.persistence.base import Base


def _utc_now() -> datetime:
    """返回 UTC 当前时间，统一 Topic Watch 的时间戳来源。"""
    return datetime.now(UTC)


class TopicWatchRow(Base):
    """研究平台的 Topic Watch 原始持久化对象。"""

    __tablename__ = "topic_watches"

    watch_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    query_terms_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    seed_papers_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    template_family: Mapped[str] = mapped_column(String(64), nullable=False)
    schedule_preset: Mapped[str] = mapped_column(String(64), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
        onupdate=_utc_now,
    )
