"""
Cleanup job — dispatches cleanup tasks for old uploads and reminders.
Triggered at 12:00 AM IST (midnight).
"""

import logging

logger = logging.getLogger("careremind.scheduler.cleanup")


def run_cleanup():
    """Dispatch cleanup tasks."""
    from celery_app import celery_app

    logger.info("🧹 Midnight — Dispatching cleanup tasks")
    celery_app.send_task("tasks.cleanup_tasks.cleanup_old_uploads")
    celery_app.send_task("tasks.cleanup_tasks.cleanup_expired_reminders")
    logger.info("Cleanup tasks dispatched")
