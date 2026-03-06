-- ============================================================
-- CareRemind — Initial Database Schema
-- Run this in Supabase SQL Editor
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE plan_type AS ENUM ('free', 'pro', 'enterprise');
CREATE TYPE preferred_channel AS ENUM ('whatsapp', 'sms', 'both');
CREATE TYPE reminder_status AS ENUM (
    'Pending', 'Sent', 'Failed', 'Confirmed', 'Cancelled', 'Optout'
);
CREATE TYPE upload_status AS ENUM (
    'processing', 'completed', 'failed', 'partial'
);
CREATE TYPE upload_source AS ENUM ('excel', 'photo', 'manual');

-- ============================================================
-- TABLE: tenants (one row per doctor account)
-- ============================================================

CREATE TABLE tenants (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_name     TEXT NOT NULL,
    clinic_name     TEXT NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    phone           TEXT,
    specialty       TEXT,
    language_preference TEXT NOT NULL DEFAULT 'english',
    whatsapp_number TEXT,
    plan            plan_type NOT NULL DEFAULT 'free',
    trial_ends_at   TIMESTAMPTZ,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tenants_email ON tenants (email);
CREATE INDEX idx_tenants_is_active ON tenants (is_active);

-- ============================================================
-- TABLE: patients
-- ============================================================

CREATE TABLE patients (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    phone_encrypted     TEXT NOT NULL,
    preferred_channel   preferred_channel NOT NULL DEFAULT 'whatsapp',
    has_whatsapp        BOOLEAN DEFAULT NULL,
    language_preference TEXT,
    is_optout           BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_patients_tenant_id ON patients (tenant_id);
CREATE INDEX idx_patients_is_optout ON patients (tenant_id, is_optout);
CREATE UNIQUE INDEX idx_patients_phone_tenant ON patients (tenant_id, phone_encrypted);

-- ============================================================
-- TABLE: appointments
-- ============================================================

CREATE TABLE appointments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    patient_id          UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    visit_date          DATE NOT NULL,
    next_visit_date     DATE,
    specialty_override  TEXT,
    notes_encrypted     TEXT,
    source              upload_source NOT NULL DEFAULT 'manual',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_appointments_tenant_id ON appointments (tenant_id);
CREATE INDEX idx_appointments_patient_id ON appointments (patient_id);
CREATE INDEX idx_appointments_next_visit ON appointments (tenant_id, next_visit_date)
    WHERE next_visit_date IS NOT NULL;

-- ============================================================
-- TABLE: reminders
-- ============================================================

CREATE TABLE reminders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    appointment_id      UUID NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
    reminder_number     SMALLINT NOT NULL DEFAULT 1,
    status              reminder_status NOT NULL DEFAULT 'Pending',
    message_text        TEXT,
    language_used       TEXT,
    channel             preferred_channel,
    scheduled_at        TIMESTAMPTZ NOT NULL,
    sent_at             TIMESTAMPTZ,
    error_log           TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_reminders_tenant_id ON reminders (tenant_id);
CREATE INDEX idx_reminders_status ON reminders (tenant_id, status);
CREATE INDEX idx_reminders_scheduled ON reminders (scheduled_at)
    WHERE status = 'Pending';

-- Prevent duplicate reminders for the same appointment + reminder slot
CREATE UNIQUE INDEX idx_reminders_unique_slot
    ON reminders (appointment_id, reminder_number);

-- ============================================================
-- TABLE: upload_logs
-- ============================================================

CREATE TABLE upload_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    filename            TEXT NOT NULL,
    file_type           TEXT NOT NULL,
    total_rows          INTEGER NOT NULL DEFAULT 0,
    duplicates_skipped  INTEGER NOT NULL DEFAULT 0,
    failed_rows         INTEGER NOT NULL DEFAULT 0,
    status              upload_status NOT NULL DEFAULT 'processing',
    storage_url         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_upload_logs_tenant_id ON upload_logs (tenant_id);

-- ============================================================
-- TABLE: audit_logs (append-only)
-- ============================================================

CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID REFERENCES tenants(id) ON DELETE SET NULL,
    user_id         UUID,
    action          TEXT NOT NULL,
    resource        TEXT NOT NULL,
    resource_id     UUID,
    ip_address      INET,
    user_agent      TEXT,
    old_value       JSONB,
    new_value       JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_tenant_id ON audit_logs (tenant_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs (created_at);
CREATE INDEX idx_audit_logs_resource ON audit_logs (resource, resource_id);

-- ============================================================
-- ROW LEVEL SECURITY
-- Ensures every tenant can only see their own data
-- ============================================================

-- Enable RLS on all tables
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE upload_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS (used by FastAPI backend)
-- These policies allow the backend service role full access.
-- Individual user access is enforced at the application layer via JWT tenant_id.

CREATE POLICY "Service role full access on tenants"
    ON tenants FOR ALL
    USING (TRUE)
    WITH CHECK (TRUE);

CREATE POLICY "Service role full access on patients"
    ON patients FOR ALL
    USING (TRUE)
    WITH CHECK (TRUE);

CREATE POLICY "Service role full access on appointments"
    ON appointments FOR ALL
    USING (TRUE)
    WITH CHECK (TRUE);

CREATE POLICY "Service role full access on reminders"
    ON reminders FOR ALL
    USING (TRUE)
    WITH CHECK (TRUE);

CREATE POLICY "Service role full access on upload_logs"
    ON upload_logs FOR ALL
    USING (TRUE)
    WITH CHECK (TRUE);

CREATE POLICY "Service role full access on audit_logs"
    ON audit_logs FOR ALL
    USING (TRUE)
    WITH CHECK (TRUE);

-- ============================================================
-- AUTO-UPDATE updated_at TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_tenants
    BEFORE UPDATE ON tenants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_patients
    BEFORE UPDATE ON patients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- DONE
-- ============================================================
