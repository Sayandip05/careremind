from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ClinicLocationBase(BaseModel):
    """Base schema for clinic location data."""
    clinic_name: str = Field(..., min_length=2, max_length=200)
    address_line: str = Field(..., min_length=5, max_length=500)
    city: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    state: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)


class ClinicLocationCreate(ClinicLocationBase):
    """Schema for creating a new clinic location."""
    pass


class ClinicLocationUpdate(BaseModel):
    """Schema for updating a clinic location."""
    clinic_name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    address_line: Optional[str] = Field(default=None, min_length=5, max_length=500)
    city: Optional[str] = Field(default=None, min_length=2, max_length=100)
    pincode: Optional[str] = Field(default=None, min_length=6, max_length=6, pattern=r"^\d{6}$")
    state: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = None


class ClinicLocationResponse(ClinicLocationBase):
    """Schema for clinic location API responses."""
    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClinicLocationListResponse(BaseModel):
    """Schema for listing clinic locations."""
    clinics: list[ClinicLocationResponse]
    total: int
