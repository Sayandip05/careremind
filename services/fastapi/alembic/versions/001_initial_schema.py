"""Initial schema — full baseline for CareRemind production database.

This is the single source of truth for the database schema.
All tables are created here in one shot.

Revision ID: 001
Revises:
Create Date: 2026-04-30

Schema overview:
  - tenants          : clinic / doctor accounts (multi-tenant root)
  - patients         : patient records per tenant
  - appointments     : appointment records per patient
  - reminders        : WhatsApp/SMS reminder records
  - upload_logs      : Excel/photo upload audit log
  - clinic_locations : multi-clinic support per tenant
  - bookings         : online appointment bookings with payment
  - daily_schedules  : generated PDF schedule records
  - audit_logs       : API-level audit trail
  - payments         : Razorpay payment records

Design decisions:
  - All IDs are VARCHAR (Python generates UUID strings via str(uuid4()))
  - All enum/status columns are VARCHAR (avoids PostgreSQL enum migration pain)
  - FKs use ON DELETE CASCADE unless semantics require SET NULL
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# ---------------------------------------------------------------------------
# Revision identifiers
# ---------------------------------------------------------------------------
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── tenants ─────────────────────────────────────────────────────────────
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("doctor_name", sa.String(), nullable=False),
        sa.Column("clinic_name", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("whatsapp_number", sa.String(), nullable=True),
        sa.Column("plan", sa.String(), nullable=False, server_default="free"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("google_id", sa.String(), nullable=True),
        # Address
        sa.Column("street", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("state", sa.String(), nullable=True),
        sa.Column("pincode", sa.String(), nullable=True),
        # Preferences
        sa.Column("language", sa.String(), nullable=True),
        sa.Column("specialty", sa.String(), nullable=True),
        sa.Column("email_marketing", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tenants_email", "tenants", ["email"], unique=True)
    op.create_index("ix_tenants_is_active", "tenants", ["is_active"], unique=False)

    # ── patients ─────────────────────────────────────────────────────────────
    op.create_table(
        "patients",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("phone_encrypted", sa.String(), nullable=False),
        sa.Column("phone_hash", sa.String(), nullable=True),
        sa.Column("preferred_channel", sa.String(), nullable=False, server_default="whatsapp"),
        sa.Column("language", sa.String(), nullable=True),
        sa.Column("is_optout", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_patients_tenant_id", "patients", ["tenant_id"], unique=False)
    op.create_index("ix_patients_phone_hash", "patients", ["phone_hash"], unique=False)
    op.create_index("ix_patients_is_optout", "patients", ["is_optout"], unique=False)

    # ── appointments ─────────────────────────────────────────────────────────
    op.create_table(
        "appointments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("patient_id", sa.String(), nullable=False),
        sa.Column("appointment_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("doctor_name", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_appointments_tenant_id", "appointments", ["tenant_id"], unique=False)
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"], unique=False)

    # ── reminders ────────────────────────────────────────────────────────────
    op.create_table(
        "reminders",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("patient_id", sa.String(), nullable=True),
        sa.Column("appointment_id", sa.String(), nullable=True),
        sa.Column("channel", sa.String(), nullable=False, server_default="whatsapp"),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("message_template", sa.String(), nullable=True),
        sa.Column("error_log", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reminders_tenant_id", "reminders", ["tenant_id"], unique=False)
    op.create_index("ix_reminders_patient_id", "reminders", ["patient_id"], unique=False)
    op.create_index("ix_reminders_appointment_id", "reminders", ["appointment_id"], unique=False)
    op.create_index("ix_reminders_status", "reminders", ["status"], unique=False)
    op.create_index("ix_reminders_scheduled_at", "reminders", ["scheduled_at"], unique=False)

    # ── upload_logs ──────────────────────────────────────────────────────────
    op.create_table(
        "upload_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),       # excel | photo
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("storage_url", sa.String(), nullable=True),
        sa.Column("total_rows", sa.Integer(), nullable=True),
        sa.Column("duplicates_skipped", sa.Integer(), nullable=True),
        sa.Column("failed_rows", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_upload_logs_tenant_id", "upload_logs", ["tenant_id"], unique=False)

    # ── clinic_locations ─────────────────────────────────────────────────────
    op.create_table(
        "clinic_locations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("clinic_name", sa.String(), nullable=False),
        sa.Column("address_line", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("pincode", sa.String(length=6), nullable=False),
        sa.Column("state", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_clinic_locations_tenant_id", "clinic_locations", ["tenant_id"], unique=False)
    op.create_index("ix_clinic_locations_is_active", "clinic_locations", ["is_active"], unique=False)

    # ── bookings ─────────────────────────────────────────────────────────────
    op.create_table(
        "bookings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("patient_id", sa.String(), nullable=False),
        sa.Column("appointment_id", sa.String(), nullable=True),
        sa.Column("clinic_location_id", sa.String(), nullable=False),
        sa.Column("booking_date", sa.Date(), nullable=False),
        sa.Column("slot_time", sa.Time(), nullable=False),
        sa.Column("serial_number", sa.Integer(), nullable=True),
        # status values: reserved | confirmed | cancelled | completed | expired
        sa.Column("status", sa.String(), nullable=False, server_default="reserved"),
        sa.Column("payment_id", sa.String(), nullable=True),
        # payment_status values: pending | completed | failed | refunded
        sa.Column("payment_status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("razorpay_order_id", sa.String(), nullable=True),
        sa.Column("razorpay_payment_id", sa.String(), nullable=True),
        sa.Column("reserved_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["clinic_location_id"], ["clinic_locations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bookings_tenant_id", "bookings", ["tenant_id"], unique=False)
    op.create_index("ix_bookings_patient_id", "bookings", ["patient_id"], unique=False)
    op.create_index("ix_bookings_clinic_location_id", "bookings", ["clinic_location_id"], unique=False)
    op.create_index("ix_bookings_booking_date", "bookings", ["booking_date"], unique=False)
    op.create_index("ix_bookings_status", "bookings", ["status"], unique=False)
    # Partial unique index — prevents double-booking the same slot
    op.create_index(
        "idx_unique_active_slot",
        "bookings",
        ["clinic_location_id", "booking_date", "slot_time"],
        unique=True,
        postgresql_where=sa.text("status IN ('reserved', 'confirmed')"),
    )

    # ── daily_schedules ──────────────────────────────────────────────────────
    op.create_table(
        "daily_schedules",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("clinic_location_id", sa.String(), nullable=False),
        sa.Column("schedule_date", sa.Date(), nullable=False),
        sa.Column("pdf_url", sa.String(), nullable=True),
        sa.Column("total_online_bookings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_walk_in_slots", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["clinic_location_id"], ["clinic_locations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_daily_schedules_tenant_id", "daily_schedules", ["tenant_id"], unique=False)
    op.create_index("ix_daily_schedules_clinic_location_id", "daily_schedules", ["clinic_location_id"], unique=False)
    op.create_index("ix_daily_schedules_schedule_date", "daily_schedules", ["schedule_date"], unique=False)

    # ── audit_logs ───────────────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=True),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("resource_type", sa.String(), nullable=True),
        sa.Column("resource_id", sa.String(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"], unique=False)
    op.create_index("ix_audit_logs_resource_id", "audit_logs", ["resource_id"], unique=False)
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)

    # ── payments ─────────────────────────────────────────────────────────────
    op.create_table(
        "payments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("razorpay_order_id", sa.String(), nullable=False),
        sa.Column("razorpay_payment_id", sa.String(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("plan", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payments_tenant_id", "payments", ["tenant_id"], unique=False)


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("payments")
    op.drop_table("audit_logs")
    op.drop_table("daily_schedules")
    op.drop_table("bookings")
    op.drop_table("clinic_locations")
    op.drop_table("upload_logs")
    op.drop_table("reminders")
    op.drop_table("appointments")
    op.drop_table("patients")
    op.drop_table("tenants")
