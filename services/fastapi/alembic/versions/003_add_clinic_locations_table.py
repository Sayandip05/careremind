"""Add clinic_locations table for multi-clinic support

Revision ID: 003
Revises: 002
Create Date: 2026-04-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: str = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create clinic_locations table
    op.create_table(
        'clinic_locations',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('clinic_name', sa.String(), nullable=False),
        sa.Column('address_line', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('pincode', sa.String(length=6), nullable=False),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index on tenant_id for faster lookups
    op.create_index('ix_clinic_locations_tenant_id', 'clinic_locations', ['tenant_id'], unique=False)

    # Create index on is_active for filtering active clinics
    op.create_index('ix_clinic_locations_is_active', 'clinic_locations', ['is_active'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_clinic_locations_is_active', table_name='clinic_locations')
    op.drop_index('ix_clinic_locations_tenant_id', table_name='clinic_locations')
    op.drop_table('clinic_locations')
