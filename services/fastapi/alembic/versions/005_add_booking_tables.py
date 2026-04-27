"""Add booking and daily_schedule tables for V2

Revision ID: 005
Revises: 004
Create Date: 2026-04-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: str = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create bookings table
    op.create_table(
        'bookings',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('appointment_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('clinic_location_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('booking_date', sa.Date(), nullable=False),
        sa.Column('slot_time', sa.Time(), nullable=False),
        sa.Column('serial_number', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('RESERVED', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'EXPIRED', name='bookingstatus'), nullable=False),
        sa.Column('payment_id', sa.String(), nullable=True),
        sa.Column('payment_status', sa.Enum('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED', name='paymentstatus'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('razorpay_order_id', sa.String(), nullable=True),
        sa.Column('razorpay_payment_id', sa.String(), nullable=True),
        sa.Column('reserved_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['clinic_location_id'], ['clinic_locations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for bookings
    op.create_index('ix_bookings_tenant_id', 'bookings', ['tenant_id'], unique=False)
    op.create_index('ix_bookings_patient_id', 'bookings', ['patient_id'], unique=False)
    op.create_index('ix_bookings_clinic_location_id', 'bookings', ['clinic_location_id'], unique=False)
    op.create_index('ix_bookings_booking_date', 'bookings', ['booking_date'], unique=False)
    op.create_index('ix_bookings_status', 'bookings', ['status'], unique=False)

    # Create daily_schedules table
    op.create_table(
        'daily_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('clinic_location_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('schedule_date', sa.Date(), nullable=False),
        sa.Column('pdf_url', sa.String(), nullable=True),
        sa.Column('total_online_bookings', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_walk_in_slots', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['clinic_location_id'], ['clinic_locations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for daily_schedules
    op.create_index('ix_daily_schedules_tenant_id', 'daily_schedules', ['tenant_id'], unique=False)
    op.create_index('ix_daily_schedules_clinic_location_id', 'daily_schedules', ['clinic_location_id'], unique=False)
    op.create_index('ix_daily_schedules_schedule_date', 'daily_schedules', ['schedule_date'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_daily_schedules_schedule_date', table_name='daily_schedules')
    op.drop_index('ix_daily_schedules_clinic_location_id', table_name='daily_schedules')
    op.drop_index('ix_daily_schedules_tenant_id', table_name='daily_schedules')

    op.drop_index('ix_bookings_status', table_name='bookings')
    op.drop_index('ix_bookings_booking_date', table_name='bookings')
    op.drop_index('ix_bookings_clinic_location_id', table_name='bookings')
    op.drop_index('ix_bookings_patient_id', table_name='bookings')
    op.drop_index('ix_bookings_tenant_id', table_name='bookings')

    op.drop_table('daily_schedules')
    op.drop_table('bookings')

    op.execute('DROP TYPE IF EXISTS paymentstatus')
    op.execute('DROP TYPE IF EXISTS bookingstatus')
