"""Add clinic address fields to tenants table

Revision ID: 002
Revises: 001
Create Date: 2026-04-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: str = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add clinic address columns
    op.add_column('tenants', sa.Column('street', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('city', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('pincode', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('state', sa.String(), nullable=True))


def downgrade() -> None:
    # Drop clinic address columns
    op.drop_column('tenants', 'state')
    op.drop_column('tenants', 'pincode')
    op.drop_column('tenants', 'city')
    op.drop_column('tenants', 'street')
