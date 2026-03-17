from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.models.staff import Staff
from app.models.tenant import Tenant

router = APIRouter()


@router.get("/")
async def list_staff(
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """List all staff members for the clinic."""
    stmt = select(Staff).where(Staff.tenant_id == tenant.id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{staff_id}")
async def get_staff_details(
    staff_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Get details for a specific staff member."""
    stmt = select(Staff).where(Staff.id == staff_id, Staff.tenant_id == tenant.id)
    result = await db.execute(stmt)
    staff = result.scalar_one_or_none()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
        
    return staff
