"""Add topic_watches table.

Revision ID: 0003_topic_watches
Revises: 0002_runs_token_usage
Create Date: 2026-07-01
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_topic_watches"
down_revision: str | Sequence[str] | None = "0002_runs_token_usage"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """升级 schema，新增 Topic Watch 表。"""
    op.create_table(
        "topic_watches",
        sa.Column("watch_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("query_terms_json", sa.JSON(), nullable=False),
        sa.Column("seed_papers_json", sa.JSON(), nullable=False),
        sa.Column("template_family", sa.String(length=64), nullable=False),
        sa.Column("schedule_preset", sa.String(length=64), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("watch_id"),
    )
    with op.batch_alter_table("topic_watches", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_topic_watches_user_id"), ["user_id"], unique=False)


def downgrade() -> None:
    """回滚 schema，删除 Topic Watch 表。"""
    with op.batch_alter_table("topic_watches", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_topic_watches_user_id"))
    op.drop_table("topic_watches")
