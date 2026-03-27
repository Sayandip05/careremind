"""
Auth Service — Business logic for registration and login.
"""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.features.auth.models import Tenant
from app.features.auth.schemas import TenantRegister, TenantUpdate, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token


async def register_tenant(data: TenantRegister, db: AsyncSession) -> Tenant:
    """
    Register a new doctor account.
    Hashes password and creates a Tenant record.
    """
    # Check if email already exists
    stmt = select(Tenant).where(Tenant.email == data.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new tenant
    tenant = Tenant(
        id=str(uuid.uuid4()),
        doctor_name=data.doctor_name,
        clinic_name=data.clinic_name,
        email=data.email,
        phone=data.phone,
        specialty=data.specialty,
        language_preference=data.language_preference or "english",
        whatsapp_number=data.whatsapp_number,
        hashed_password=get_password_hash(data.password),
        is_active=True,
    )
    
    db.add(tenant)
    await db.flush()
    return tenant


async def authenticate_tenant(username: str, password: str, db: AsyncSession) -> TokenResponse:
    """
    Authenticate a doctor and return a JWT token.
    """
    stmt = select(Tenant).where(Tenant.email == username, Tenant.is_active.is_(True))
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant or not verify_password(password, tenant.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate token
    token = create_access_token(tenant_id=tenant.id, email=tenant.email)
    
    return TokenResponse(
        access_token=token,
        tenant_id=tenant.id,
        doctor_name=tenant.doctor_name,
    )


async def update_profile(tenant: Tenant, data: TenantUpdate, db: AsyncSession) -> Tenant:
    """
    Update editable fields on a tenant profile.
    Only non-None fields from TenantUpdate are applied.
    """
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(tenant, field, value)

    await db.flush()
    await db.refresh(tenant)
    return tenant
