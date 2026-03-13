"""
APScheduler — cron-based job scheduler for CareRemind.
Dispatches Celery tasks at specific times (IST timezone).

Schedule:
    9:00 AM  — Send pending reminders
    9:30 AM  — Send daily summary to doctors
    11:00 AM — Retry failed reminders
    12:00 AM — Cleanup old records
"""

import os
import sys
import logging
from pathlib import Path

# Add worker to path for celery imports
WORKER_DIR = str(Path(__file__).resolve().parent.parent / "worker")
if WORKER_DIR not in sys.path:
    sys.path.insert(0, WORKER_DIR)

# Add FastAPI to path for dotenv
FASTAPI_DIR = str(Path(__file__).resolve().parent.parent / "fastapi")
if FASTAPI_DIR not in sys.path:
    sys.path.insert(0, FASTAPI_DIR)

from dotenv import load_dotenv
load_dotenv(Path(FASTAPI_DIR) / ".env")

from apscheduler.schedulers.blocking import BlockingScheduler
from jobs.daily_reminder_job import run_daily_reminder
from jobs.summary_report_job import run_summary_report
from jobs.retry_failed_job import run_retry_failed
from jobs.cleanup_job import run_cleanup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("careremind.scheduler")

scheduler = BlockingScheduler(timezone="Asia/Kolkata")

# ── Scheduled Jobs ────────────────────────────────────────
scheduler.add_job(
    run_daily_reminder,
    "cron", hour=9, minute=0,
    id="daily_reminders",
    name="Send pending reminders",
    misfire_grace_time=600,  # 10 min grace if scheduler was down
)

scheduler.add_job(
    run_summary_report,
    "cron", hour=9, minute=30,
    id="daily_summary",
    name="Send daily summary to doctors",
    misfire_grace_time=600,
)

scheduler.add_job(
    run_retry_failed,
    "cron", hour=11, minute=0,
    id="retry_failed",
    name="Retry failed reminders",
    misfire_grace_time=600,
)

scheduler.add_job(
    run_cleanup,
    "cron", hour=0, minute=0,
    id="midnight_cleanup",
    name="Cleanup old records",
    misfire_grace_time=3600,  # 1 hr grace for cleanup
)


if __name__ == "__main__":
    logger.info("CareRemind Scheduler starting — IST timezone")
    logger.info("Scheduled jobs:")
    for job in scheduler.get_jobs():
        logger.info("  [%s] %s — next run: %s", job.id, job.name, job.next_run_time)
    scheduler.start()
