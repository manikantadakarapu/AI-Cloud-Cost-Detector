"""analysis jobs

Revision ID: 20260601_0003
Revises: 20260601_0002
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260601_0003"
down_revision: str | None = "20260601_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("analyses", sa.Column("job_id", sa.String(length=128), nullable=True))
    op.add_column("analyses", sa.Column("progress_percentage", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("analyses", sa.Column("current_stage", sa.String(length=64), nullable=True))
    op.add_column("analyses", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("analyses", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("analyses", sa.Column("error_message", sa.Text(), nullable=True))
    op.create_index(op.f("ix_analyses_job_id"), "analyses", ["job_id"], unique=False)
    op.create_index(op.f("ix_analyses_status"), "analyses", ["status"], unique=False)
    op.alter_column("analyses", "status", server_default="queued")


def downgrade() -> None:
    op.alter_column("analyses", "status", server_default=None)
    op.drop_index(op.f("ix_analyses_status"), table_name="analyses")
    op.drop_index(op.f("ix_analyses_job_id"), table_name="analyses")
    op.drop_column("analyses", "error_message")
    op.drop_column("analyses", "completed_at")
    op.drop_column("analyses", "started_at")
    op.drop_column("analyses", "current_stage")
    op.drop_column("analyses", "progress_percentage")
    op.drop_column("analyses", "job_id")
