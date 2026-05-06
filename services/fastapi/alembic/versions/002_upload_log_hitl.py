"""Add file_hash and extracted_data to upload_logs.

Revision ID: 002
Revises: 001
Create Date: 2026-05-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add file_hash column — SHA-256 hex digest for idempotency checks
    op.add_column(
        "upload_logs",
        sa.Column("file_hash", sa.String(64), nullable=True),
    )
    op.create_index("ix_upload_logs_file_hash", "upload_logs", ["file_hash"])

    # Add extracted_data column — JSON blob for human-in-the-loop review storage
    op.add_column(
        "upload_logs",
        sa.Column("extracted_data", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_index("ix_upload_logs_file_hash", table_name="upload_logs")
    op.drop_column("upload_logs", "file_hash")
    op.drop_column("upload_logs", "extracted_data")
