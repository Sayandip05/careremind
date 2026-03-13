"""
Daily reminder job — dispatches Celery task to send all pending reminders.
Triggered at 9:00 AM IST.
"""

import logging

logger = logging.getLogger("careremind.scheduler.daily_reminder")


def run_daily_reminder():
    """Dispatch the send_pending_reminders Celery task."""
    from celery_app import celery_app

    logger.info("⏰ 9:00 AM — Dispatching send_pending_reminders task")
    result = celery_app.send_task("tasks.reminder_tasks.send_pending_reminders")
    logger.info("Task dispatched: %s", result.id)
