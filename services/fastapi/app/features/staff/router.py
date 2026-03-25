import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.features.staff.models import Staff
from app.features.auth.models import Tenant

logger = logging.getLogger("careremind.staff")

router = APIRouter()


@router.get("/")
async def list_staff(
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """List all staff members for the clinic."""
    try:
        stmt = select(Staff).where(Staff.tenant_id == tenant.id)
        result = await db.execute(stmt)
        staff = result.scalars().all()
        return staff
    except Exception as e:
        logger.error("Failed to fetch staff list: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch staff list",
        )


@router.get("/{staff_id}")
async def get_staff_details(
    staff_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Get details for a specific staff member."""
    try:
        stmt = select(Staff).where(Staff.id == staff_id, Staff.tenant_id == tenant.id)
        result = await db.execute(stmt)
        staff = result.scalar_one_or_none()

        if not staff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff member not found",
            )

        return staff
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch staff details: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch staff details",
        )
