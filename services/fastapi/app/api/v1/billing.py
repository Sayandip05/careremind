from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.models.payment import Payment
from app.models.tenant import Tenant
from app.schemas.payment import PaymentResponse

router = APIRouter()


@router.get("/history", response_model=list[PaymentResponse])
async def get_payment_history(
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Get all payments for the authenticated tenant."""
    stmt = select(Payment).where(Payment.tenant_id == tenant.id).order_by(Payment.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/status")
async def get_subscription_status(
    tenant: Tenant = Depends(get_current_tenant),
):
    """Check current plan and trial status."""
    return {
        "plan": tenant.plan,
        "is_active": tenant.is_active,
        "trial_ends_at": tenant.trial_ends_at,
    }
