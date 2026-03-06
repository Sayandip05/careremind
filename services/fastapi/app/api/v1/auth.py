"""
Auth routes — JWT verification and tenant profile.
Django handles login/registration. FastAPI only verifies tokens.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.models.tenant import Tenant
from app.schemas.tenant import TenantResponse, TenantUpdate
from app.services import tenant_service

router = APIRouter()


@router.get("/me", response_model=TenantResponse)
async def get_my_profile(
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Returns the authenticated doctor's profile.
    Validates that the JWT is valid and the account is active.
    """
    return tenant


@router.patch("/me", response_model=TenantResponse)
async def update_my_profile(
    data: TenantUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Update the authenticated doctor's profile."""
    updated = await tenant_service.update_profile(tenant, data, db)
    return updated
