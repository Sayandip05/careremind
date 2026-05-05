"""
Queue helpers for CareRemind.

The canonical Celery application lives in app.worker.celery_app.
Import from there — do NOT define a second Celery instance here.
"""

from app.worker.celery_app import celery_app  # re-export for convenience

__all__ = ["celery_app"]
