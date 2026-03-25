"""
Typed state schemas for all LangGraph agent graphs.
Each graph has its own TypedDict that flows through nodes.
"""

from __future__ import annotations

from typing import Any, Optional

from typing_extensions import TypedDict


# ── Ingestion Pipeline State ────────────────────────────────
class IngestionState(TypedDict, total=False):
    """State flowing through the ingestion graph (upload → extract → dedup → save)."""

    # Inputs
    file_type: str              # "excel" | "photo"
    file_bytes: bytes
    tenant_id: str
    db: Any                     # AsyncSession (not serializable, passed by ref)

    # Set by router
    source: str                 # UploadSource enum value

    # Set by extraction nodes
    extracted_rows: list[dict]
    extraction_errors: list[str]
    extraction_skipped: int
    total_rows: int

    # Set by dedup node
    new_rows: list[dict]
    duplicate_rows: list[dict]

    # Set by save node
    saved_count: int
    save_errors: list[str]


# ── Notification Pipeline State ─────────────────────────────
class NotificationState(TypedDict, total=False):
    """State flowing through the notification graph (load → optout check → generate → send)."""

    # Inputs
    reminder: Any               # Reminder ORM object
    db: Any                     # AsyncSession

    # Loaded by context node
    appointment: Any            # Appointment ORM object
    patient: Any                # Patient ORM object
    tenant: Any                 # Tenant ORM object

    # Set by decrypt node
    phone: Optional[str]

    # Set by message node
    message: Optional[str]

    # Set by send nodes
    channel: Optional[str]      # "whatsapp" | "sms"
    status: str                 # "sent" | "failed" | "optout" | "error"
    error: Optional[str]
    success: bool


# ── Scheduling Pipeline State ───────────────────────────────
class SchedulingState(TypedDict, total=False):
    """State flowing through the scheduling graph (specialty → timing → create reminders)."""

    # Inputs
    appointment: Any            # Appointment ORM object
    tenant: Any                 # Tenant ORM object
    db: Any                     # AsyncSession

    # Set by specialty node
    specialty_name: str
    specialty: Any              # BaseSpecialty object
    timings: list               # list of ReminderTiming objects

    # Set by create node
    created_reminders: list     # list of Reminder ORM objects
    skipped_count: int
