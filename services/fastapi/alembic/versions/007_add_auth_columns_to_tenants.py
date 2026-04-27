"""Add hashed_password and email_marketing to tenants table

Revision ID: 007
Revises: 006
Create Date: 2026-04-26

These two columns were in the SQLAlchemy Tenant model but were never
added to the Supabase table via SQL, causing login to fail with
UndefinedColumnError.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: str = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add hashed_password column (nullable=True first so existing rows don't break,
    # we'll set a placeholder then tighten if needed)
    op.add_column('tenants', sa.Column('hashed_password', sa.String(), nullable=True))

    # Add email_marketing column with a safe default
    op.add_column('tenants', sa.Column('email_marketing', sa.Boolean(), nullable=False, server_default=sa.text('true')))


def downgrade() -> None:
    op.drop_column('tenants', 'email_marketing')
    op.drop_column('tenants', 'hashed_password')
