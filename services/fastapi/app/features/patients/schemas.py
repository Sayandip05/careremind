from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    """Schema for creating a new patient."""
    name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=10, max_length=15, description="Indian phone number (10 digits)")
    preferred_channel: str = Field(default="whatsapp", pattern="^(whatsapp|sms|both)$")
    language_preference: Optional[str] = None


class PatientUpdate(BaseModel):
    """Schema for updating a patient."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=15)
    preferred_channel: Optional[str] = Field(default=None, pattern="^(whatsapp|sms|both)$")
    language_preference: Optional[str] = None


class PatientResponse(BaseModel):
    """Schema for patient data in API responses. Phone is never exposed."""
    id: str
    name: str
    preferred_channel: str
    has_whatsapp: Optional[bool]
    language_preference: Optional[str]
    is_optout: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PatientListResponse(BaseModel):
    """Paginated patient list."""
    patients: list[PatientResponse]
    total: int
    page: int
    per_page: int
