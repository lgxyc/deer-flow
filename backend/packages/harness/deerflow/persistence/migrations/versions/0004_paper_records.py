"""新增 paper_records 表。

Revision ID: 0004_paper_records
Revises: 0003_topic_watches
Create Date: 2026-07-01
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004_paper_records"
down_revision: str | Sequence[str] | None = "0003_topic_watches"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """升级 schema，新增 Paper Record 表。"""
    op.create_table(
        "paper_records",
        sa.Column("paper_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("source_name", sa.String(length=32), nullable=False),
        sa.Column("source_paper_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("abstract", sa.Text(), nullable=False),
        sa.Column("authors_json", sa.JSON(), nullable=False),
        sa.Column("categories_json", sa.JSON(), nullable=False),
        sa.Column("discovered_watch_ids_json", sa.JSON(), nullable=False),
        sa.Column("matched_query_terms_json", sa.JSON(), nullable=False),
        sa.Column("published_at", sa.String(length=32), nullable=True),
        sa.Column("source_updated_at", sa.String(length=32), nullable=True),
        sa.Column("source_abs_url", sa.Text(), nullable=False),
        sa.Column("source_pdf_url", sa.Text(), nullable=True),
        sa.Column("pdf_status", sa.String(length=32), nullable=False),
        sa.Column("pdf_relative_path", sa.Text(), nullable=True),
        sa.Column("pdf_error", sa.Text(), nullable=True),
        sa.Column("raw_source_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("paper_id"),
        sa.UniqueConstraint(
            "user_id",
            "source_name",
            "source_paper_id",
            name="uq_paper_records_user_source_paper",
        ),
    )
    with op.batch_alter_table("paper_records", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_paper_records_user_id"), ["user_id"], unique=False)


def downgrade() -> None:
    """回滚 schema，删除 Paper Record 表。"""
    with op.batch_alter_table("paper_records", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_paper_records_user_id"))
    op.drop_table("paper_records")
