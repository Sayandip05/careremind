from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Registration & Auth ──────────────────────────────────────

class TenantRegister(BaseModel):
    """Schema for doctor registration."""
    doctor_name: str = Field(..., min_length=2, max_length=100)
    clinic_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    phone: Optional[str] = None
    specialty: Optional[str] = None
    language_preference: str = Field(default="english")
    whatsapp_number: Optional[str] = None
    password: str = Field(..., min_length=8)
    # Clinic address (optional)
    street: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None



class TokenResponse(BaseModel):
    """JWT token response — includes user data so frontend doesn't need a second call."""
    access_token: str
    token_type: str = "bearer"
    tenant_id: str
    doctor_name: str
    clinic_name: str = ""
    email: str = ""
    specialty: Optional[str] = None
    plan: str = "free"


class TenantLogin(BaseModel):
    """Schema for doctor login."""
    email: EmailStr
    password: str



# ── Tenant CRUD ──────────────────────────────────────────────

class TenantUpdate(BaseModel):
    """Schema for updating tenant profile."""
    doctor_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    clinic_name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    phone: Optional[str] = None
    specialty: Optional[str] = None
    language_preference: Optional[str] = None
    whatsapp_number: Optional[str] = None
    # Clinic address
    street: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None


class TenantResponse(BaseModel):
    """Schema for tenant data in API responses."""
    id: str
    doctor_name: str
    clinic_name: str
    email: str
    phone: Optional[str]
    specialty: Optional[str]
    language_preference: str
    whatsapp_number: Optional[str]
    plan: str
    is_active: bool
    created_at: datetime
    # Clinic address
    street: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None

    model_config = {"from_attributes": True}
