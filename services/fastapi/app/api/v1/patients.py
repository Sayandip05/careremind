"""
Patient routes — CRUD with encryption, dedup, and IDOR protection.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.models.tenant import Tenant
from app.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from app.services import patient_service

router = APIRouter()


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """List all patients for the authenticated doctor (paginated)."""
    patients, total = await patient_service.list_patients(
        tenant_id=str(tenant.id),
        db=db,
        page=page,
        per_page=per_page,
    )
    return PatientListResponse(
        patients=[PatientResponse.model_validate(p) for p in patients],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("/", response_model=PatientResponse, status_code=201)
async def create_patient(
    data: PatientCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new patient.
    Phone number is encrypted before storage. Duplicate phones are rejected.
    """
    patient = await patient_service.create_patient(
        tenant_id=str(tenant.id),
        data=data,
        db=db,
    )
    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single patient by ID.
    IDOR protected — only the owning doctor can access.
    """
    patient = await patient_service.get_patient(
        tenant_id=str(tenant.id),
        patient_id=patient_id,
        db=db,
    )
    return patient


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    data: PatientUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a patient.
    IDOR protected — only the owning doctor can modify.
    """
    patient = await patient_service.update_patient(
        tenant_id=str(tenant.id),
        patient_id=patient_id,
        data=data,
        db=db,
    )
    return patient
