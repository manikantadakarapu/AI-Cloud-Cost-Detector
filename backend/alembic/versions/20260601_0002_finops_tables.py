"""finops tables

Revision ID: 20260601_0002
Revises: 20260601_0001
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260601_0002"
down_revision: str | None = "20260601_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "analysis_costs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("analysis_id", sa.Uuid(), nullable=False),
        sa.Column("resource_id", sa.Text(), nullable=False),
        sa.Column("service_name", sa.String(length=256), nullable=False),
        sa.Column("resource_name", sa.String(length=512), nullable=False),
        sa.Column("cost_amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("billing_period", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analysis_costs_analysis_id"), "analysis_costs", ["analysis_id"], unique=False)
    op.create_index(op.f("ix_analysis_costs_billing_period"), "analysis_costs", ["billing_period"], unique=False)
    op.create_index(op.f("ix_analysis_costs_resource_id"), "analysis_costs", ["resource_id"], unique=False)
    op.create_index(op.f("ix_analysis_costs_service_name"), "analysis_costs", ["service_name"], unique=False)
    op.create_index(
        "ix_analysis_costs_analysis_resource_period",
        "analysis_costs",
        ["analysis_id", "resource_id", "billing_period"],
        unique=False,
    )

    op.create_table(
        "analysis_findings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("analysis_id", sa.Uuid(), nullable=False),
        sa.Column("resource_id", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("estimated_monthly_savings", sa.Numeric(18, 6), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analysis_findings_analysis_id"), "analysis_findings", ["analysis_id"], unique=False)
    op.create_index(op.f("ix_analysis_findings_category"), "analysis_findings", ["category"], unique=False)
    op.create_index(op.f("ix_analysis_findings_resource_id"), "analysis_findings", ["resource_id"], unique=False)
    op.create_index(op.f("ix_analysis_findings_severity"), "analysis_findings", ["severity"], unique=False)
    op.create_index(
        "ix_analysis_findings_analysis_category_severity",
        "analysis_findings",
        ["analysis_id", "category", "severity"],
        unique=False,
    )

    op.create_table(
        "finops_scores",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("analysis_id", sa.Uuid(), nullable=False),
        sa.Column("overall_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("compute_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("storage_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("network_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("recommendation_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_finops_scores_analysis_id"), "finops_scores", ["analysis_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_finops_scores_analysis_id"), table_name="finops_scores")
    op.drop_table("finops_scores")
    op.drop_index("ix_analysis_findings_analysis_category_severity", table_name="analysis_findings")
    op.drop_index(op.f("ix_analysis_findings_severity"), table_name="analysis_findings")
    op.drop_index(op.f("ix_analysis_findings_resource_id"), table_name="analysis_findings")
    op.drop_index(op.f("ix_analysis_findings_category"), table_name="analysis_findings")
    op.drop_index(op.f("ix_analysis_findings_analysis_id"), table_name="analysis_findings")
    op.drop_table("analysis_findings")
    op.drop_index("ix_analysis_costs_analysis_resource_period", table_name="analysis_costs")
    op.drop_index(op.f("ix_analysis_costs_service_name"), table_name="analysis_costs")
    op.drop_index(op.f("ix_analysis_costs_resource_id"), table_name="analysis_costs")
    op.drop_index(op.f("ix_analysis_costs_billing_period"), table_name="analysis_costs")
    op.drop_index(op.f("ix_analysis_costs_analysis_id"), table_name="analysis_costs")
    op.drop_table("analysis_costs")
