import uuid
import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UploadStatus(str, enum.Enum):
    PROCESSING = "processing"
    PENDING_REVIEW = "pending_review"   # Photo extracted, awaiting doctor confirmation
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class UploadLog(Base):
    __tablename__ = "upload_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(
        String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_hash = Column(String(64), nullable=True, index=True)  # SHA-256 hex — idempotency key
    total_rows = Column(Integer, nullable=False, default=0)
    duplicates_skipped = Column(Integer, nullable=False, default=0)
    failed_rows = Column(Integer, nullable=False, default=0)
    status = Column(Enum(UploadStatus, values_callable=lambda x: [e.value for e in x], native_enum=False), nullable=False, default=UploadStatus.PROCESSING)
    storage_url = Column(String)
    extracted_data = Column(Text, nullable=True)  # JSON — extracted rows pending review
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="upload_logs")
