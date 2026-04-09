# ── Models Package ───────────────────────────────────────────
# Import all models here so Alembic and other modules can do:
#   from app.models import Tenant, Patient, ...

from app.features.auth.models import Tenant, PlanType
from app.features.patients.models import Patient, PreferredChannel
from app.features.appointments.models import Appointment, UploadSource
from app.features.reminders.models import Reminder, ReminderStatus, ChannelType
from app.features.upload.models import UploadLog, UploadStatus
from app.features.audit.models import AuditLog
from app.features.billing.models import Payment
from app.features.staff.models import Staff
from app.features.clinics.models import ClinicLocation
from app.features.booking.models import Booking, BookingStatus, PaymentStatus, DailySchedule

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
    "Staff",
    "ClinicLocation",
    "Booking",
    "BookingStatus",
    "PaymentStatus",
    "DailySchedule",
]
