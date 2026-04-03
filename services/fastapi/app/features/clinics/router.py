"""
Clinic Location routes — CRUD for managing doctor's clinic locations.
Supports multiple clinics per tenant.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.features.auth.models import Tenant
from app.features.clinics.schemas import (
    ClinicLocationCreate,
    ClinicLocationListResponse,
    ClinicLocationResponse,
    ClinicLocationUpdate,
)
from app.features.clinics import service as clinic_service

logger = logging.getLogger("careremind.clinics")

router = APIRouter()


@router.get("/", response_model=ClinicLocationListResponse)
async def list_clinics(
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    List all clinic locations for the authenticated doctor.
    Returns active clinics by default.
    """
    try:
        clinics = await clinic_service.list_clinic_locations(
            tenant_id=str(tenant.id),
            db=db,
            include_inactive=False,
        )
        return ClinicLocationListResponse(
            clinics=[ClinicLocationResponse.model_validate(c) for c in clinics],
            total=len(clinics),
        )
    except Exception as e:
        logger.error("Failed to fetch clinic locations: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch clinic locations",
        )


@router.post("/", response_model=ClinicLocationResponse, status_code=201)
async def create_clinic(
    data: ClinicLocationCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new clinic location.
    
    Doctors can have multiple clinics (e.g., "City Clinic", "Morning Clinic").
    """
    try:
        clinic = await clinic_service.create_clinic_location(
            tenant_id=str(tenant.id),
            data=data,
            db=db,
        )
        return clinic
    except Exception as e:
        logger.error("Failed to create clinic location: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create clinic location",
        )


@router.get("/{clinic_id}", response_model=ClinicLocationResponse)
async def get_clinic(
    clinic_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single clinic location by ID.
    IDOR protected — only the owning doctor can access.
    """
    try:
        clinic = await clinic_service.get_clinic_location(
            tenant_id=str(tenant.id),
            clinic_id=clinic_id,
            db=db,
        )
        return clinic
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch clinic location: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch clinic location",
        )


@router.patch("/{clinic_id}", response_model=ClinicLocationResponse)
async def update_clinic(
    clinic_id: str,
    data: ClinicLocationUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a clinic location.
    IDOR protected — only the owning doctor can modify.
    """
    try:
        clinic = await clinic_service.update_clinic_location(
            tenant_id=str(tenant.id),
            clinic_id=clinic_id,
            data=data,
            db=db,
        )
        return clinic
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update clinic location: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update clinic location",
        )


@router.delete("/{clinic_id}", status_code=204)
async def delete_clinic(
    clinic_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete (deactivate) a clinic location.
    IDOR protected — only the owning doctor can delete.
    
    Note: This performs a soft delete by setting is_active=False.
    """
    try:
        await clinic_service.delete_clinic_location(
            tenant_id=str(tenant.id),
            clinic_id=clinic_id,
            db=db,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete clinic location: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete clinic location",
        )
