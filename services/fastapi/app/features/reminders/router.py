"""
Reminder routes — List reminders with status filtering.
Reminders are created by the system (scheduler/agents), not by the doctor directly.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.features.reminders.models import Reminder, ReminderStatus
from app.features.auth.models import Tenant
from app.features.reminders.schemas import ReminderListResponse, ReminderResponse

logger = logging.getLogger("careremind.reminders")

router = APIRouter()


@router.get("/", response_model=ReminderListResponse)
async def list_reminders(
    status: Optional[str] = Query(
        default=None, description="Filter by status: Pending, Sent, Failed, etc."
    ),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """List reminders for the authenticated doctor (paginated, filterable by status)."""
    try:
        tenant_id = str(tenant.id)

        base_query = select(Reminder).where(Reminder.tenant_id == tenant_id)
        count_query = select(func.count(Reminder.id)).where(
            Reminder.tenant_id == tenant_id
        )

        if status:
            try:
                status_enum = ReminderStatus(status)
                base_query = base_query.where(Reminder.status == status_enum)
                count_query = count_query.where(Reminder.status == status_enum)
            except ValueError:
                logger.warning("Invalid status filter: %s", status)

        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        offset = (page - 1) * per_page
        result = await db.execute(
            base_query.order_by(Reminder.scheduled_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        reminders = list(result.scalars().all())

        return ReminderListResponse(
            reminders=[ReminderResponse.model_validate(r) for r in reminders],
            total=total,
            page=page,
            per_page=per_page,
        )
    except Exception as e:
        logger.error("Failed to fetch reminders: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch reminders")
