"""
Celery application configuration for CareRemind.

This module is the single entry point for the Celery worker.
The worker container starts with:
    celery -A app.worker.celery_app worker --loglevel=info

Because the worker builds from the same image as the API server,
all app.* imports work without any sys.path manipulation.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery("careremind")

celery_app.conf.update(
    # ── Broker & Backend ────────────────────────────────────────
    broker_url=settings.REDIS_URL,
    result_backend=settings.REDIS_URL,

    # ── Serialization ────────────────────────────────────────────
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # ── Time ─────────────────────────────────────────────────────
    timezone="Asia/Kolkata",
    enable_utc=True,

    # ── Reliability ──────────────────────────────────────────────
    task_track_started=True,
    task_acks_late=True,          # Re-queue task if worker crashes mid-execution
    worker_prefetch_multiplier=4, # Prefetch 4 tasks per worker for throughput

    # ── Timeouts ─────────────────────────────────────────────────
    task_soft_time_limit=300,     # 5 min soft limit — raises SoftTimeLimitExceeded
    task_time_limit=600,          # 10 min hard limit — kills the task process

    # ── Results ──────────────────────────────────────────────────
    result_expires=3600,          # Task results expire after 1 hour (prevent Redis bloat)
)

# Auto-discover all tasks inside app/worker/tasks/
celery_app.autodiscover_tasks(["app.worker.tasks"])
