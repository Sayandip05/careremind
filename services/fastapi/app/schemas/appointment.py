from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class AppointmentCreate(BaseModel):
    """Schema for creating a new appointment."""
    patient_id: str
    visit_date: date
    next_visit_date: Optional[date] = None
    specialty_override: Optional[str] = None
    notes: Optional[str] = None
    source: str = Field(default="manual", pattern="^(excel|photo|manual)$")


class AppointmentResponse(BaseModel):
    """Schema for appointment data in API responses."""
    id: str
    patient_id: str
    visit_date: date
    next_visit_date: Optional[date]
    specialty_override: Optional[str]
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AppointmentListResponse(BaseModel):
    """Paginated appointment list."""
    appointments: list[AppointmentResponse]
    total: int
    page: int
    per_page: int
