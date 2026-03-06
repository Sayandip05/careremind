"""
Tenant Service — Business logic for tenant profile management.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.schemas.tenant import TenantUpdate


async def get_profile(tenant: Tenant) -> Tenant:
    """Return the tenant object (already loaded by get_current_tenant dependency)."""
    return tenant


async def update_profile(
    tenant: Tenant,
    data: TenantUpdate,
    db: AsyncSession,
) -> Tenant:
    """
    Update tenant profile. Only provided fields are updated.
    """
    if data.doctor_name is not None:
        tenant.doctor_name = data.doctor_name

    if data.clinic_name is not None:
        tenant.clinic_name = data.clinic_name

    if data.phone is not None:
        tenant.phone = data.phone

    if data.specialty is not None:
        tenant.specialty = data.specialty

    if data.language_preference is not None:
        tenant.language_preference = data.language_preference

    if data.whatsapp_number is not None:
        tenant.whatsapp_number = data.whatsapp_number

    await db.flush()
    return tenant
