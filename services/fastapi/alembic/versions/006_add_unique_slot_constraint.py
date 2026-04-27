"""add unique slot constraint for race condition protection

Revision ID: 006
Revises: 005
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Add partial unique index to prevent double-booking
    # Only applies to RESERVED and CONFIRMED bookings
    op.create_index(
        'idx_unique_active_slot',
        'bookings',
        ['clinic_location_id', 'booking_date', 'slot_time'],
        unique=True,
        postgresql_where=sa.text("status IN ('RESERVED', 'CONFIRMED')")
    )


def downgrade():
    op.drop_index('idx_unique_active_slot', table_name='bookings')
