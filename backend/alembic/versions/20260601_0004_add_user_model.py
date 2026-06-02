"""Add User model

Revision ID: 0004_add_user_model
Revises: 0003_analysis_jobs
Create Date: 2026-06-01 12:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0004_add_user_model'
down_revision: str | None = '0003_analysis_jobs'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('azure_object_id', sa.String(length=128), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('display_name', sa.String(length=256), nullable=False),
    sa.Column('role', sa.String(length=64), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_azure_object_id'), 'users', ['azure_object_id'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_azure_object_id'), table_name='users')
    op.drop_table('users')
