"""
Clinic Location Service — Business logic for managing doctor's clinic locations.
Supports multiple clinics per tenant with full CRUD operations.
"""

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ForbiddenException
from app.features.clinics.models import ClinicLocation
from app.features.clinics.schemas import ClinicLocationCreate, ClinicLocationUpdate


async def list_clinic_locations(
    tenant_id: str,
    db: AsyncSession,
    include_inactive: bool = False,
) -> list[ClinicLocation]:
    """
    List all clinic locations for a tenant.
    
    Args:
        tenant_id: The tenant's ID
        db: Database session
        include_inactive: If True, include inactive clinics
    
    Returns:
        List of ClinicLocation objects
    """
    stmt = select(ClinicLocation).where(ClinicLocation.tenant_id == tenant_id)
    
    if not include_inactive:
        stmt = stmt.where(ClinicLocation.is_active.is_(True))
    
    stmt = stmt.order_by(ClinicLocation.created_at.desc())
    
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_clinic_location(
    tenant_id: str,
    clinic_id: str,
    db: AsyncSession,
) -> ClinicLocation:
    """
    Get a single clinic location by ID.
    
    IDOR protection: verifies clinic belongs to the requesting tenant.
    
    Args:
        tenant_id: The tenant's ID
        clinic_id: The clinic location ID
        db: Database session
    
    Returns:
        ClinicLocation object
    
    Raises:
        NotFoundException: If clinic not found
        ForbiddenException: If clinic belongs to another tenant
    """
    result = await db.execute(
        select(ClinicLocation).where(ClinicLocation.id == clinic_id)
    )
    clinic = result.scalar_one_or_none()
    
    if not clinic:
        raise NotFoundException("Clinic location not found")
    
    if str(clinic.tenant_id) != str(tenant_id):
        raise ForbiddenException("Clinic location does not belong to your account")
    
    return clinic


async def create_clinic_location(
    tenant_id: str,
    data: ClinicLocationCreate,
    db: AsyncSession,
) -> ClinicLocation:
    """
    Create a new clinic location for a tenant.
    
    Args:
        tenant_id: The tenant's ID
        data: ClinicLocationCreate schema
        db: Database session
    
    Returns:
        Created ClinicLocation object
    """
    clinic = ClinicLocation(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        clinic_name=data.clinic_name,
        address_line=data.address_line,
        city=data.city,
        pincode=data.pincode,
        state=data.state,
        phone=data.phone,
        is_active=True,
    )
    
    db.add(clinic)
    await db.flush()
    return clinic


async def update_clinic_location(
    tenant_id: str,
    clinic_id: str,
    data: ClinicLocationUpdate,
    db: AsyncSession,
) -> ClinicLocation:
    """
    Update a clinic location.
    
    IDOR protection: verifies clinic belongs to the requesting tenant.
    Only provided fields are updated.
    
    Args:
        tenant_id: The tenant's ID
        clinic_id: The clinic location ID
        data: ClinicLocationUpdate schema
        db: Database session
    
    Returns:
        Updated ClinicLocation object
    """
    clinic = await get_clinic_location(tenant_id, clinic_id, db)
    
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(clinic, field, value)
    
    await db.flush()
    return clinic


async def delete_clinic_location(
    tenant_id: str,
    clinic_id: str,
    db: AsyncSession,
) -> None:
    """
    Delete (soft delete by deactivating) a clinic location.
    
    IDOR protection: verifies clinic belongs to the requesting tenant.
    
    Note: We soft delete by setting is_active=False to preserve historical data.
    For hard delete, use db.delete(clinic).
    
    Args:
        tenant_id: The tenant's ID
        clinic_id: The clinic location ID
        db: Database session
    """
    clinic = await get_clinic_location(tenant_id, clinic_id, db)
    
    # Soft delete - set inactive
    clinic.is_active = False
    await db.flush()


async def hard_delete_clinic_location(
    tenant_id: str,
    clinic_id: str,
    db: AsyncSession,
) -> None:
    """
    Permanently delete a clinic location.
    
    Use with caution - this removes the record entirely.
    
    Args:
        tenant_id: The tenant's ID
        clinic_id: The clinic location ID
        db: Database session
    """
    clinic = await get_clinic_location(tenant_id, clinic_id, db)
    
    await db.delete(clinic)
    await db.flush()
