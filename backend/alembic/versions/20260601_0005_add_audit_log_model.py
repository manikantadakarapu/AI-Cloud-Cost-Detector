"""Add AuditLog model

Revision ID: 0005_add_audit_log_model
Revises: 0004_add_user_model
Create Date: 2026-06-01 12:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0005_add_audit_log_model'
down_revision: str | None = '0004_add_user_model'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('audit_logs',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('actor_user_id', sa.String(length=128), nullable=False),
    sa.Column('target_user_id', sa.String(length=128), nullable=True),
    sa.Column('action', sa.String(length=128), nullable=False),
    sa.Column('details', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_actor_user_id'), 'audit_logs', ['actor_user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_target_user_id'), 'audit_logs', ['target_user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_target_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_actor_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_table('audit_logs')
