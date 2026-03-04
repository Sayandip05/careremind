from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from app.core.database import Base


class UploadLog(Base):
    __tablename__ = "upload_logs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    filename = Column(String)
    file_type = Column(String)
    total_rows = Column(Integer, default=0)
    duplicates_skipped = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    status = Column(String)
    s3_url = Column(String)
    created_at = Column(DateTime, server_default=func.now())
