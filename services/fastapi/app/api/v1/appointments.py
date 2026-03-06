"""
Appointment routes — CRUD with IDOR protection on patient ownership.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.models.tenant import Tenant
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentListResponse,
    AppointmentResponse,
)
from app.services import appointment_service

router = APIRouter()


@router.get("/", response_model=AppointmentListResponse)
async def list_appointments(
    patient_id: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """List appointments for the authenticated doctor (paginated, filterable by patient)."""
    appointments, total = await appointment_service.list_appointments(
        tenant_id=str(tenant.id),
        db=db,
        patient_id=patient_id,
        page=page,
        per_page=per_page,
    )
    return AppointmentListResponse(
        appointments=[AppointmentResponse.model_validate(a) for a in appointments],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    data: AppointmentCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new appointment.
    IDOR protected — verifies the patient_id belongs to the authenticated doctor.
    """
    appointment = await appointment_service.create_appointment(
        tenant_id=str(tenant.id),
        data=data,
        db=db,
    )
    return appointment
