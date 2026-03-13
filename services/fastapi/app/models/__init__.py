# ── Models Package ───────────────────────────────────────────
# Import all models here so Alembic and other modules can do:
#   from app.models import Tenant, Patient, ...

from app.models.tenant import Tenant, PlanType
from app.models.patient import Patient, PreferredChannel
from app.models.appointment import Appointment, UploadSource
from app.models.reminder import Reminder, ReminderStatus, ChannelType
from app.models.upload_log import UploadLog, UploadStatus
from app.models.audit_log import AuditLog
from app.models.payment import Payment

__all__ = [
    "Tenant",
    "PlanType",
    "Patient",
    "PreferredChannel",
    "Appointment",
    "UploadSource",
    "Reminder",
    "ReminderStatus",
    "ChannelType",
    "UploadLog",
    "UploadStatus",
    "AuditLog",
    "Payment",
]
