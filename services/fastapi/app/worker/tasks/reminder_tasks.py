"""
Reminder tasks — send pending reminders via WhatsApp.
Called by the scheduler at 9:00 AM IST daily.
"""

import asyncio
import logging
from datetime import datetime, timezone

from celery import shared_task
from sqlalchemy import select

logger = logging.getLogger("careremind.worker.reminders")


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def send_pending_reminders(self):
    """
    Fetch all PENDING reminders where scheduled_at <= now and send them.
    """
    return asyncio.run(_send_pending())


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def send_single_reminder(self, reminder_id: str):
    """Send a specific reminder by ID."""
    return asyncio.run(_send_single(reminder_id))


@shared_task(bind=True, max_retries=1)
def retry_failed_reminders(self):
    """
    Retry all FAILED reminders (max 2 attempts).
    Called by scheduler at 11:00 AM IST.
    """
    return asyncio.run(_retry_failed())


async def _send_pending():
    """Fetch and send all due reminders."""
    from app.core.database import async_session
    from app.features.reminders.models import Reminder, ReminderStatus
    from app.features.reminders.service import notification_service

    async with async_session() as db:
        try:
            now = datetime.now(timezone.utc)
            result = await db.execute(
                select(Reminder).where(
                    Reminder.status == ReminderStatus.PENDING,
                    Reminder.scheduled_at <= now,
                ).order_by(Reminder.scheduled_at).limit(500)
            )
            reminders = result.scalars().all()

            sent = 0
            failed = 0

            for reminder in reminders:
                try:
                    outcome = await notification_service.send_reminder(reminder, db)
                    if outcome["success"]:
                        sent += 1
                    else:
                        failed += 1
                        reminder.retry_count += 1
                except Exception as e:
                    logger.error("Error sending reminder %s: %s", reminder.id, e)
                    failed += 1
                    reminder.retry_count += 1

            await db.commit()
            logger.info("Sent %d reminders, %d failed", sent, failed)
            return {"sent": sent, "failed": failed, "total": len(reminders)}
        except Exception as e:
            await db.rollback()
            logger.error("Database error in _send_pending: %s", e)
            raise


async def _send_single(reminder_id: str):
    """Send one specific reminder."""
    from app.core.database import async_session
    from app.features.reminders.models import Reminder
    from app.features.reminders.service import notification_service

    async with async_session() as db:
        try:
            reminder = await db.get(Reminder, reminder_id)
            if not reminder:
                return {"success": False, "error": "Reminder not found"}

            outcome = await notification_service.send_reminder(reminder, db)
            await db.commit()
            return outcome
        except Exception as e:
            await db.rollback()
            logger.error(
                "Database error in _send_single for reminder %s: %s", reminder_id, e
            )
            raise


async def _retry_failed():
    """Retry failed reminders (only those with retry_count < 2)."""
    from app.core.database import async_session
    from app.features.reminders.models import Reminder, ReminderStatus
    from app.features.reminders.service import notification_service

    async with async_session() as db:
        try:
            result = await db.execute(
                select(Reminder).where(
                    Reminder.status == ReminderStatus.FAILED,
                    Reminder.retry_count < 2,
                ).limit(200)
            )
            reminders = result.scalars().all()

            retried = 0
            for reminder in reminders:
                reminder.retry_count += 1
                reminder.status = ReminderStatus.PENDING
                reminder.error_log = None
                try:
                    outcome = await notification_service.send_reminder(reminder, db)
                    if outcome["success"]:
                        retried += 1
                except Exception as e:
                    logger.error("Retry error for %s: %s", reminder.id, e)

            await db.commit()
            logger.info(
                "Retried %d of %d failed reminders", retried, len(reminders)
            )
            return {"retried": retried, "total_failed": len(reminders)}
        except Exception as e:
            await db.rollback()
            logger.error("Database error in _retry_failed: %s", e)
            raise
