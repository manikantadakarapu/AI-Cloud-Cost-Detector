"""initial schema

Revision ID: 20260601_0001
Revises:
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260601_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "analyses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("subscription_id", sa.String(length=128), nullable=False),
        sa.Column("resource_group", sa.String(length=256), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analyses_resource_group"), "analyses", ["resource_group"], unique=False)
    op.create_index(op.f("ix_analyses_subscription_id"), "analyses", ["subscription_id"], unique=False)

    op.create_table(
        "resources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("analysis_id", sa.Uuid(), nullable=False),
        sa.Column("resource_id", sa.Text(), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("type", sa.String(length=256), nullable=False),
        sa.Column("location", sa.String(length=128), nullable=True),
        sa.Column("sku", sa.String(length=256), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resources_analysis_id"), "resources", ["analysis_id"], unique=False)
    op.create_index(op.f("ix_resources_type"), "resources", ["type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_resources_type"), table_name="resources")
    op.drop_index(op.f("ix_resources_analysis_id"), table_name="resources")
    op.drop_table("resources")
    op.drop_index(op.f("ix_analyses_subscription_id"), table_name="analyses")
    op.drop_index(op.f("ix_analyses_resource_group"), table_name="analyses")
    op.drop_table("analyses")
