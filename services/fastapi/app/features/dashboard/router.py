"""
Dashboard routes — Aggregated stats in a single DB query.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.features.patients.models import Patient
from app.features.reminders.models import Reminder, ReminderStatus
from app.features.upload.models import UploadLog
from app.features.auth.models import Tenant

logger = logging.getLogger("careremind.dashboard")

router = APIRouter()


from app.core.cache import cache
import json

@router.get("/stats")
async def get_dashboard_stats(
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Dashboard statistics — single round-trip to the database.
    Returns patient count, reminder counts by status, and upload count.
    Cached in Redis for 5 minutes.
    """
    try:
        tenant_id = str(tenant.id)
        cache_key = f"dashboard_stats:{tenant_id}"
        
        # 1. Attempt Cache Retrieval
        try:
            cached_data = await cache.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning("Redis cache get bypassed [%s]: %s", cache_key, e)

        # 2. Database Fetch
        result = await db.execute(
            select(
                func.count(func.distinct(Patient.id))
                .filter(Patient.tenant_id == tenant_id)
                .label("total_patients"),
                func.count(func.distinct(Reminder.id))
                .filter(
                    Reminder.tenant_id == tenant_id,
                    Reminder.status == ReminderStatus.PENDING,
                )
                .label("pending_reminders"),
                func.count(func.distinct(Reminder.id))
                .filter(
                    Reminder.tenant_id == tenant_id,
                    Reminder.status == ReminderStatus.SENT,
                )
                .label("sent_reminders"),
                func.count(func.distinct(Reminder.id))
                .filter(
                    Reminder.tenant_id == tenant_id,
                    Reminder.status == ReminderStatus.FAILED,
                )
                .label("failed_reminders"),
                func.count(func.distinct(UploadLog.id))
                .filter(UploadLog.tenant_id == tenant_id)
                .label("total_uploads"),
            ).select_from(
                Patient.__table__.outerjoin(
                    Reminder, Reminder.tenant_id == Patient.tenant_id
                ).outerjoin(UploadLog, UploadLog.tenant_id == Patient.tenant_id)
            )
        )
        row = result.one()

        total_sent = row.sent_reminders or 0
        total_failed = row.failed_reminders or 0
        total_attempted = total_sent + total_failed

        stats = {
            "total_patients": row.total_patients or 0,
            "pending_reminders": row.pending_reminders or 0,
            "sent_reminders": total_sent,
            "failed_reminders": total_failed,
            "success_rate": round((total_sent / total_attempted * 100), 1)
            if total_attempted > 0
            else 0,
            "total_uploads": row.total_uploads or 0,
        }

        # 3. Store in Cache (5 minutes)
        try:
            await cache.set(cache_key, json.dumps(stats), ex=300)
        except Exception as e:
            logger.warning("Redis cache set bypassed [%s]: %s", cache_key, e)

        return stats
    except Exception as e:
        logger.error("Failed to fetch dashboard stats: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard stats")
