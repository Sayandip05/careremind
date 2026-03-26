"""
Cleanup tasks — remove old uploads and archive expired reminders.
Runs daily at midnight.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from celery import shared_task

logger = logging.getLogger("careremind.worker.cleanup")


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task
def cleanup_old_uploads():
    """Delete upload records and files older than 30 days."""
    return _run_async(_cleanup_uploads())


@shared_task
def cleanup_expired_reminders():
    """Archive reminders older than 90 days (already sent or failed)."""
    return _run_async(_cleanup_reminders())


async def _cleanup_uploads():
    """Remove upload_logs older than 30 days."""
    from app.core.database import async_session
    from app.features.upload.models import UploadLog
    from sqlalchemy import delete

    cutoff = datetime.now(timezone.utc) - timedelta(days=30)

    async with async_session() as db:
        result = await db.execute(
            delete(UploadLog).where(UploadLog.created_at < cutoff)
        )
        deleted = result.rowcount
        await db.commit()

    logger.info("Cleaned up %d old upload records", deleted)
    return {"deleted_uploads": deleted}


async def _cleanup_reminders():
    """Delete completed/failed reminders older than 90 days."""
    from app.core.database import async_session
    from app.features.reminders.models import Reminder, ReminderStatus
    from sqlalchemy import delete

    cutoff = datetime.now(timezone.utc) - timedelta(days=90)

    async with async_session() as db:
        result = await db.execute(
            delete(Reminder).where(
                Reminder.created_at < cutoff,
                Reminder.status.in_([ReminderStatus.SENT, ReminderStatus.FAILED, ReminderStatus.OPTOUT]),
            )
        )
        deleted = result.rowcount
        await db.commit()

    logger.info("Cleaned up %d old reminders", deleted)
    return {"deleted_reminders": deleted}
