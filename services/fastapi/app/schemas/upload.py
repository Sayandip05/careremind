from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Schema returned immediately after file upload is accepted."""
    upload_id: str
    status: str
    filename: str


class UploadDetailResponse(BaseModel):
    """Schema for detailed upload status (after processing)."""
    id: str
    filename: str
    file_type: str
    total_rows: int
    duplicates_skipped: int
    failed_rows: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UploadListResponse(BaseModel):
    """Paginated upload history."""
    uploads: list[UploadDetailResponse]
    total: int
    page: int
    per_page: int
