"""Add phone_hash column to patients table

Revision ID: 001
Revises: 
Create Date: 2026-04-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add phone_hash column
    op.add_column('patients', sa.Column('phone_hash', sa.String(), nullable=True))
    
    # Create index on phone_hash for fast dedup lookups
    op.create_index('ix_patients_phone_hash', 'patients', ['phone_hash'], unique=False)
    
    # Note: For existing data, you would need to backfill phone_hash by:
    # 1. Decrypting each phone_encrypted with the current key
    # 2. Computing hash using encryption_service.hash_phone(phone)
    # 3. Updating the phone_hash column
    # This is a one-time migration script that should be run after deployment.
    
    # Make phone_hash non-nullable after backfill (if needed)
    # op.alter_column('patients', 'phone_hash', nullable=False)


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_patients_phone_hash', table_name='patients')
    
    # Drop column
    op.drop_column('patients', 'phone_hash')
