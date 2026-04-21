import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.features.billing.models import Payment
from app.features.auth.models import Tenant
from app.features.billing.schemas import PaymentResponse

logger = logging.getLogger("careremind.billing")

router = APIRouter()


@router.get("/history")
async def get_payment_history(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Records per page"),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated payment history for the authenticated tenant."""
    try:
        base_stmt = select(Payment).where(Payment.tenant_id == tenant.id)

        # Total count for pagination metadata
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # Paginated records
        offset = (page - 1) * per_page
        stmt = (
            base_stmt
            .order_by(Payment.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await db.execute(stmt)
        payments = result.scalars().all()

        return {
            "data": [PaymentResponse.model_validate(p) for p in payments],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
            },
        }
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

