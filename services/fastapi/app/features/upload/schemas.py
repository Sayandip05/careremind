from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


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


# ── Human-in-the-Loop Review Schemas ─────────────────────────────────────────


class ReviewedPatientRow(BaseModel):
    """A single patient row the doctor has reviewed and confirmed."""

    name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=10, max_length=15)
    visit_date: Optional[date] = None
    next_visit_date: Optional[date] = None


class PhotoConfirmRequest(BaseModel):
    """
    Sent by the doctor after reviewing extracted OCR rows.
    Only the rows included here will be saved to the database.
    """

    upload_id: str
    confirmed_rows: list[ReviewedPatientRow]


class PhotoExtractResponse(BaseModel):
    """
    Returned immediately after photo upload.
    Contains extracted rows for doctor review — nothing is saved yet.
    """

    upload_id: str
    status: str  # "pending_review" | "failed"
    filename: str
    extracted_rows: list[dict]  # Raw extracted data for display
    total_extracted: int
    errors: list[str]
    provider: str  # Which VLM processed the image
