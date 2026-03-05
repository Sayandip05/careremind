# ── Schemas Package ──────────────────────────────────────────
from app.schemas.tenant import (
    TenantRegister,
    LoginRequest,
    TokenResponse,
    TenantUpdate,
    TenantResponse,
)
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
)
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentListResponse,
)
from app.schemas.reminder import (
    ReminderResponse,
    ReminderListResponse,
)
from app.schemas.upload import (
    UploadResponse,
    UploadDetailResponse,
    UploadListResponse,
)

__all__ = [
    "TenantRegister",
    "LoginRequest",
    "TokenResponse",
    "TenantUpdate",
    "TenantResponse",
    "PatientCreate",
    "PatientUpdate",
    "PatientResponse",
    "PatientListResponse",
    "AppointmentCreate",
    "AppointmentResponse",
    "AppointmentListResponse",
    "ReminderResponse",
    "ReminderListResponse",
    "UploadResponse",
    "UploadDetailResponse",
    "UploadListResponse",
]
