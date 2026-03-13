"""
Auth routes — registration, login, and tenant profile.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.models.tenant import Tenant
from app.schemas.tenant import TenantResponse, TenantUpdate, TenantRegister, TenantLogin, TokenResponse
from app.services import auth_service

router = APIRouter()


@router.post("/register", response_model=TenantResponse)
async def register(
    data: TenantRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new doctor account.
    Consolidates functionality.
    """
    tenant = await auth_service.register_tenant(data, db)
    return tenant


@router.post("/login", response_model=TokenResponse)
async def login(
    data: TenantLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a doctor and return a JWT.
    Consolidates functionality.
    """
    return await auth_service.authenticate_tenant(data, db)



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
