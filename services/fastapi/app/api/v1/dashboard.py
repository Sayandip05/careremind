"""
Dashboard routes — Aggregated stats in a single DB query.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, literal, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.models.patient import Patient
from app.models.reminder import Reminder, ReminderStatus
from app.models.upload_log import UploadLog
from app.models.tenant import Tenant

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Dashboard statistics — single round-trip to the database.
    Returns patient count, reminder counts by status, and upload count.
    """
    tenant_id = str(tenant.id)

    # Single query: count patients, pending/sent/failed reminders, uploads
    result = await db.execute(
        select(
            # Patients
            func.count(func.distinct(Patient.id))
            .filter(Patient.tenant_id == tenant_id)
            .label("total_patients"),
            # Pending reminders
            func.count(func.distinct(Reminder.id))
            .filter(
                Reminder.tenant_id == tenant_id,
                Reminder.status == ReminderStatus.PENDING,
            )
            .label("pending_reminders"),
            # Sent reminders
            func.count(func.distinct(Reminder.id))
            .filter(
                Reminder.tenant_id == tenant_id,
                Reminder.status == ReminderStatus.SENT,
            )
            .label("sent_reminders"),
            # Failed reminders
            func.count(func.distinct(Reminder.id))
            .filter(
                Reminder.tenant_id == tenant_id,
                Reminder.status == ReminderStatus.FAILED,
            )
            .label("failed_reminders"),
            # Total uploads
            func.count(func.distinct(UploadLog.id))
            .filter(UploadLog.tenant_id == tenant_id)
            .label("total_uploads"),
        ).select_from(
            # Left joins so we get zeros instead of nulls for empty tables
            Patient.__table__
            .outerjoin(Reminder, Reminder.tenant_id == Patient.tenant_id)
            .outerjoin(UploadLog, UploadLog.tenant_id == Patient.tenant_id)
        )
    )
    row = result.one()

    total_sent = row.sent_reminders or 0
    total_failed = row.failed_reminders or 0
    total_attempted = total_sent + total_failed

    return {
        "total_patients": row.total_patients or 0,
        "pending_reminders": row.pending_reminders or 0,
        "sent_reminders": total_sent,
        "failed_reminders": total_failed,
        "success_rate": round((total_sent / total_attempted * 100), 1) if total_attempted > 0 else 0,
        "total_uploads": row.total_uploads or 0,
    }
