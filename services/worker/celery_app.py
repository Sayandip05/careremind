"""
Celery app configuration.
Uses Redis as broker. Imports FastAPI's models/services via sys.path.
"""

import sys
from pathlib import Path

# Add FastAPI app to Python path so we can import models/services
FASTAPI_DIR = str(Path(__file__).resolve().parent.parent / "fastapi")
if FASTAPI_DIR not in sys.path:
    sys.path.insert(0, FASTAPI_DIR)

# Load environment variables from FastAPI's .env
from dotenv import load_dotenv
load_dotenv(Path(FASTAPI_DIR) / ".env")

# Import settings from FastAPI config
from app.core.config import settings

from celery import Celery

# Use settings from config.py (consistent with FastAPI)
celery_app = Celery("careremind-worker")

celery_app.conf.update(
    broker_url=settings.REDIS_URL,
    result_backend=settings.REDIS_URL,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,  # Re-queue if worker crashes
    worker_prefetch_multiplier=1,  # One task at a time per worker
    task_soft_time_limit=300,  # 5 min soft limit
    task_time_limit=600,  # 10 min hard limit
)

celery_app.autodiscover_tasks(["tasks"])
