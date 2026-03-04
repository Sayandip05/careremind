from pydantic import BaseModel
from typing import Optional


class TenantCreate(BaseModel):
    clinic_name: str
    email: str
    specialty: Optional[str] = None
    language_preference: Optional[str] = "english"


class TenantResponse(BaseModel):
    id: str
    clinic_name: str
    email: str
    specialty: Optional[str]
    language_preference: str
    plan: str
    is_active: bool
