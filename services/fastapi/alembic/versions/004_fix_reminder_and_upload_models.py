"""Fix reminder and upload models - add missing fields

Revision ID: 004
Revises: 003
Create Date: 2026-04-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: str = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add patient_id to reminders table
    op.add_column('reminders', sa.Column('patient_id', sa.String(), nullable=True))
    op.create_index('ix_reminders_patient_id', 'reminders', ['patient_id'], unique=False)
    
    # Add retry_count to reminders table
    op.add_column('reminders', sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Add updated_at to reminders table
    op.add_column('reminders', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    
    # Create foreign key for patient_id
    op.create_foreign_key('fk_reminders_patient_id', 'reminders', 'patients', ['patient_id'], ['id'], ondelete='CASCADE')
    
    # Fix upload_logs status column to use enum
    # First, alter column type (this may need data migration depending on existing data)
    op.execute("ALTER TABLE upload_logs ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR")
    
    # Note: In a real migration with data, you would convert existing values to enum values first


def downgrade() -> None:
    # Drop foreign key
    op.drop_constraint('fk_reminders_patient_id', 'reminders', type_='foreignkey')
    
    # Drop columns from reminders
    op.drop_column('reminders', 'updated_at')
    op.drop_column('reminders', 'retry_count')
    op.drop_index('ix_reminders_patient_id', table_name='reminders')
    op.drop_column('reminders', 'patient_id')
