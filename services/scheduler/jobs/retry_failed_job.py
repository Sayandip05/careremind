"""
Retry failed job — dispatches retry of failed reminders.
Triggered at 11:00 AM IST.
"""

import logging

logger = logging.getLogger("careremind.scheduler.retry_failed")


def run_retry_failed():
    """Dispatch the retry_failed_reminders Celery task."""
    from celery_app import celery_app

    logger.info("🔄 11:00 AM — Dispatching retry_failed_reminders task")
    result = celery_app.send_task("tasks.reminder_tasks.retry_failed_reminders")
    logger.info("Task dispatched: %s", result.id)
