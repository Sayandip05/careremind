from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AppointmentCreate(BaseModel):
    patient_id: str
    visit_date: datetime
    next_visit_date: Optional[datetime] = None
    specialty_override: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: str
    patient_id: str
    visit_date: datetime
    next_visit_date: Optional[datetime]
    source: str
