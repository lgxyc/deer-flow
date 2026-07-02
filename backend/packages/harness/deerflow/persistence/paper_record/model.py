"""Paper Record ORM 模型。"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from deerflow.persistence.base import Base


def _utc_now() -> datetime:
    """返回 UTC 当前时间，统一 Paper Record 的时间戳来源。"""
    return datetime.now(UTC)


class PaperRecordRow(Base):
    """研究平台的 Paper Record 原始持久化对象。"""

    __tablename__ = "paper_records"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "source_name",
            "source_paper_id",
            name="uq_paper_records_user_source_paper",
        ),
    )

    paper_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String(32), nullable=False)
    source_paper_id: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False, default="")
    authors_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    categories_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    discovered_watch_ids_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    matched_query_terms_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    published_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_updated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_abs_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_status: Mapped[str] = mapped_column(String(32), nullable=False, default="missing")
    pdf_relative_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_source_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
        onupdate=_utc_now,
    )
