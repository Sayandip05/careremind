"""
Celery application configuration for CareRemind.

Entry point for the Celery worker container:
    celery -A app.worker.celery_app worker --loglevel=info -Q careremind

Broker & backend: Upstash Redis (TLS).
The `rediss://` scheme (double-s) is mandatory — plain `redis://` connections
are rejected by Upstash.  The broker_use_ssl block tells Celery's Kombu layer
to validate the server certificate against the system CA bundle.

Queue isolation: every task is routed to the 'careremind' queue so this
project does not interfere with other services sharing the same Upstash
Redis instance.
"""

import ssl

from celery import Celery

from app.core.config import settings

celery_app = Celery("careremind")

# ── SSL transport options (only applied when using TLS) ──────────────────────
_ssl_opts: dict = {}
if settings.redis_is_tls:
    _ssl_opts = {
        "broker_use_ssl": {
            "ssl_cert_reqs": ssl.CERT_REQUIRED,
        },
        "redis_backend_use_ssl": {
            "ssl_cert_reqs": ssl.CERT_REQUIRED,
        },
    }

celery_app.conf.update(
    # ── Broker & Backend ──────────────────────────────────────────────────
    broker_url=settings.UPSTASH_REDIS_URL,
    result_backend=settings.UPSTASH_REDIS_URL,

    # ── TLS (populated only for rediss:// URLs) ───────────────────────────
    **_ssl_opts,

    # ── Queue isolation ───────────────────────────────────────────────────
    # Route all tasks to 'careremind' so we don't bleed into other projects
    # that share the same Upstash instance.
    task_default_queue="careremind",
    task_queues={
        "careremind": {"exchange": "careremind", "routing_key": "careremind"},
    },

    # ── Serialization ─────────────────────────────────────────────────────
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # ── Time ──────────────────────────────────────────────────────────────
    timezone="Asia/Kolkata",
    enable_utc=True,

    # ── Reliability ───────────────────────────────────────────────────────
    task_track_started=True,
    task_acks_late=True,           # Re-queue on worker crash mid-execution
    worker_prefetch_multiplier=4,  # Prefetch 4 tasks per worker for throughput

    # ── Timeouts ──────────────────────────────────────────────────────────
    task_soft_time_limit=300,      # 5 min — raises SoftTimeLimitExceeded
    task_time_limit=600,           # 10 min hard kill

    # ── Results ───────────────────────────────────────────────────────────
    result_expires=3600,           # Expire after 1 h to prevent Redis bloat
)

# Auto-discover all tasks declared inside app/worker/tasks/
celery_app.autodiscover_tasks(["app.worker.tasks"])
