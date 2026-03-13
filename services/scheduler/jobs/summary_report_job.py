"""
Summary report job — dispatches daily summary generation for all tenants.
Triggered at 9:30 AM IST.
"""

import logging

logger = logging.getLogger("careremind.scheduler.summary_report")


def run_summary_report():
    """Dispatch the generate_daily_summary Celery task (for all tenants)."""
    from celery_app import celery_app

    logger.info("📊 9:30 AM — Dispatching generate_daily_summary task")
    result = celery_app.send_task("tasks.report_tasks.generate_daily_summary")
    logger.info("Task dispatched: %s", result.id)
