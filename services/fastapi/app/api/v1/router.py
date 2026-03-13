from fastapi import APIRouter
from app.api.v1 import (
    auth, upload, patients, appointments, reminders, 
    dashboard, webhooks, health, agent, billing,
    audit, staff
)

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(billing.router, prefix="/billing", tags=["billing"])
router.include_router(audit.router, prefix="/audit", tags=["audit"])
router.include_router(staff.router, prefix="/staff", tags=["staff"])
router.include_router(patients.router, prefix="/patients", tags=["patients"])

router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
router.include_router(upload.router, prefix="/upload", tags=["upload"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(agent.router, prefix="/agent", tags=["agent"])
