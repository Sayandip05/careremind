from fastapi import APIRouter
from app.api.v1 import upload, reminders, patients, dashboard, webhooks, health, agent

router = APIRouter()

router.include_router(upload.router, prefix="/upload", tags=["upload"])
router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
router.include_router(patients.router, prefix="/patients", tags=["patients"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(agent.router, prefix="/agent", tags=["agent"])
