import uuid
import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UploadStatus(str, enum.Enum):
    PROCESSING = "processing"
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
    total_rows = Column(Integer, nullable=False, default=0)
    duplicates_skipped = Column(Integer, nullable=False, default=0)
    failed_rows = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default=UploadStatus.PROCESSING.value)
    storage_url = Column(String)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="upload_logs")
