"""Add multi-tenancy support - add tenant_id to all tables

Revision ID: 0006_add_multi_tenancy
Revises: 0005_add_audit_log_model
Create Date: 2026-06-03 00:01:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0006_add_multi_tenancy'
down_revision: str | None = '0005_add_audit_log_model'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add tenant_id to users table
    op.add_column('users', sa.Column('tenant_id', sa.String(length=128), nullable=False, server_default=''))
    op.create_index(op.f('ix_users_tenant_id'), 'users', ['tenant_id'], unique=False)
    op.create_index('ix_users_tenant_azure_object_id', 'users', ['tenant_id', 'azure_object_id'], unique=True)
    # Drop old unique constraint on azure_object_id
    op.drop_index('ix_users_azure_object_id', table_name='users')
    # Drop old unique constraint on email
    op.drop_index('ix_users_email', table_name='users')

    # Add tenant_id to analyses table
    op.add_column('analyses', sa.Column('tenant_id', sa.String(length=128), nullable=False, server_default=''))
    op.create_index(op.f('ix_analyses_tenant_id'), 'analyses', ['tenant_id'], unique=False)
    op.create_index('ix_analyses_tenant_subscription', 'analyses', ['tenant_id', 'subscription_id'], unique=False)

    # Add tenant_id to resources table
    op.add_column('resources', sa.Column('tenant_id', sa.String(length=128), nullable=False, server_default=''))
    op.create_index(op.f('ix_resources_tenant_id'), 'resources', ['tenant_id'], unique=False)
    op.create_index('ix_resources_tenant_analysis', 'resources', ['tenant_id', 'analysis_id'], unique=False)

    # Add tenant_id to analysis_findings table
    op.add_column('analysis_findings', sa.Column('tenant_id', sa.String(length=128), nullable=False, server_default=''))
    op.create_index(op.f('ix_analysis_findings_tenant_id'), 'analysis_findings', ['tenant_id'], unique=False)
    op.create_index('ix_findings_tenant_analysis', 'analysis_findings', ['tenant_id', 'analysis_id'], unique=False)

    # Add tenant_id to analysis_costs table
    op.add_column('analysis_costs', sa.Column('tenant_id', sa.String(length=128), nullable=False, server_default=''))
    op.create_index(op.f('ix_analysis_costs_tenant_id'), 'analysis_costs', ['tenant_id'], unique=False)
    op.create_index('ix_costs_tenant_analysis', 'analysis_costs', ['tenant_id', 'analysis_id'], unique=False)

    # Add tenant_id to finops_scores table
    op.add_column('finops_scores', sa.Column('tenant_id', sa.String(length=128), nullable=False, server_default=''))
    op.create_index(op.f('ix_finops_scores_tenant_id'), 'finops_scores', ['tenant_id'], unique=False)
    op.create_index('ix_scores_tenant_analysis', 'finops_scores', ['tenant_id', 'analysis_id'], unique=False)

    # Add tenant_id to audit_logs table
    op.add_column('audit_logs', sa.Column('tenant_id', sa.String(length=128), nullable=False, server_default=''))
    op.create_index(op.f('ix_audit_logs_tenant_id'), 'audit_logs', ['tenant_id'], unique=False)
    op.create_index('ix_audit_logs_tenant_action', 'audit_logs', ['tenant_id', 'action'], unique=False)


def downgrade() -> None:
    # Downgrade audit_logs
    op.drop_index('ix_audit_logs_tenant_action', table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_tenant_id'), table_name='audit_logs')
    op.drop_column('audit_logs', 'tenant_id')

    # Downgrade finops_scores
    op.drop_index('ix_scores_tenant_analysis', table_name='finops_scores')
    op.drop_index(op.f('ix_finops_scores_tenant_id'), table_name='finops_scores')
    op.drop_column('finops_scores', 'tenant_id')

    # Downgrade analysis_costs
    op.drop_index('ix_costs_tenant_analysis', table_name='analysis_costs')
    op.drop_index(op.f('ix_analysis_costs_tenant_id'), table_name='analysis_costs')
    op.drop_column('analysis_costs', 'tenant_id')

    # Downgrade analysis_findings
    op.drop_index('ix_findings_tenant_analysis', table_name='analysis_findings')
    op.drop_index(op.f('ix_analysis_findings_tenant_id'), table_name='analysis_findings')
    op.drop_column('analysis_findings', 'tenant_id')

    # Downgrade resources
    op.drop_index('ix_resources_tenant_analysis', table_name='resources')
    op.drop_index(op.f('ix_resources_tenant_id'), table_name='resources')
    op.drop_column('resources', 'tenant_id')

    # Downgrade analyses
    op.drop_index('ix_analyses_tenant_subscription', table_name='analyses')
    op.drop_index(op.f('ix_analyses_tenant_id'), table_name='analyses')
    op.drop_column('analyses', 'tenant_id')

    # Downgrade users
    op.drop_index('ix_users_tenant_azure_object_id', table_name='users')
    op.drop_index(op.f('ix_users_tenant_id'), table_name='users')
    op.drop_column('users', 'tenant_id')
    # Restore old unique indexes
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_azure_object_id', 'users', ['azure_object_id'], unique=True)
