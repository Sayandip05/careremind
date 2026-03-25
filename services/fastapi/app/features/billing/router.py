import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.features.billing.models import Payment
from app.features.auth.models import Tenant
from app.features.billing.schemas import PaymentResponse

logger = logging.getLogger("careremind.billing")

router = APIRouter()


@router.get("/history", response_model=list[PaymentResponse])
async def get_payment_history(
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Get all payments for the authenticated tenant."""
    try:
        stmt = (
            select(Payment)
            .where(Payment.tenant_id == tenant.id)
            .order_by(Payment.created_at.desc())
        )
        result = await db.execute(stmt)
        payments = result.scalars().all()
        return payments
    except Exception as e:
        logger.error("Failed to fetch payment history: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment history",
        )


@router.get("/status")
async def get_subscription_status(
    tenant: Tenant = Depends(get_current_tenant),
):
    """Check current plan and trial status."""
    try:
        return {
            "plan": tenant.plan,
            "is_active": tenant.is_active,
            "trial_ends_at": tenant.trial_ends_at,
        }
    except Exception as e:
        logger.error("Failed to fetch subscription status: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription status",
        )
