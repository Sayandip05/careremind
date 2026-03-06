# Phase 1: Foundation — Walkthrough

> **Session:** 2026-03-05  
> **Scope:** Supabase SQL schema + FastAPI core + Models + Schemas  
> **Files changed:** 20 files (1 new, 19 modified)

---

## What Was Done

### 1. Supabase SQL Migration (NEW)

**File:** [001_initial_schema.sql](file:///c:/Users/sayan/AI%20ML/careremind/supabase/migrations/001_initial_schema.sql)

Created the complete database schema ready to paste into Supabase SQL Editor:

| Table | Key Features |
|-------|-------------|
| `tenants` | UUID PK, `doctor_name`, `password_hash`, `plan` enum, `updated_at` trigger |
| `patients` | `phone_encrypted`, `preferred_channel` enum, `has_whatsapp` |
| `appointments` | DATE types for visits, `source` (excel/photo/manual) |
| `reminders` | `reminder_status` enum, `channel`, unique constraint on [(appointment_id, reminder_number)](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/tenant.py#17-40) |
| `upload_logs` | `upload_status` enum, `storage_url` |
| `audit_logs` | JSONB for old/new values, `ON DELETE SET NULL` (survives tenant deletion) |

**Also includes:**
- 3 PostgreSQL enums (`plan_type`, `preferred_channel`, `reminder_status`)
- Row Level Security (RLS) enabled on all 6 tables
- Partial indexes for performance (e.g., pending reminders by `scheduled_at`)
- Auto-update `updated_at` trigger on `tenants` and `patients`

---

### 2. FastAPI Core (4 files rewritten)

| File | What Changed |
|------|-------------|
| [config.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/config.py) | Added all env vars from README (Supabase, FAST2SMS, CORS, ENVIRONMENT). Added [cors_origin_list](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/config.py#71-75) property and [is_production](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/config.py#76-79) check. Uses `.env` auto-loading. |
| [database.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/database.py) | Rewrote from **sync** to **async** SQLAlchemy (`asyncpg`). Connection pooling (5+10). Auto-commit on success, rollback on exception. `pool_pre_ping` for stale connection detection. |
| [security.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/security.py) | **bcrypt** password hashing (replaced `hashlib`). JWT create/verify via `python-jose`. Fernet field encryption for PII. [get_current_tenant](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/security.py#99-130) FastAPI dependency (validates JWT → loads tenant from DB). |
| [exceptions.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/exceptions.py) | Now inherits from `HTTPException` directly. Added [ForbiddenException](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/exceptions.py#25-30) (403), [ConflictException](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/exceptions.py#32-37) (409), [ValidationException](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/exceptions.py#39-44) (422). |

---

### 3. SQLAlchemy Models (7 files updated)

All models now match the README database schema exactly:

- **[tenant.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/tenant.py)** — Added `doctor_name`, `password_hash`, `phone`, `updated_at`, ORM relationships
- **[patient.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/patient.py)** — Added `preferred_channel` enum, `has_whatsapp`, `updated_at`, ORM relationships
- **[appointment.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/appointment.py)** — Changed to `Date` types (not DateTime), added cascade FK, ORM relationships
- **[reminder.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/reminder.py)** — Added `channel` enum ([ChannelType](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/reminder.py#19-22)), `created_at`, ORM relationships
- **[upload_log.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/upload_log.py)** — Renamed `s3_url` → `storage_url`, added [UploadStatus](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/upload_log.py#10-15) enum
- **[audit_log.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/audit_log.py)** — Changed to JSONB for old/new values, `ON DELETE SET NULL`
- **[__init__.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/tests/__init__.py)** — Central export of all models and enums

---

### 4. Pydantic Schemas (6 files updated)

- **[tenant.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/tenant.py)** — [TenantRegister](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/tenant.py#9-19) (with password), [LoginRequest](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/tenant.py#21-25), [TokenResponse](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/tenant.py#27-33), [TenantUpdate](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/tenant.py#37-45), [TenantResponse](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/tenant.py#47-62)
- **[patient.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/patient.py)** — [PatientCreate](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/patient.py#7-13), [PatientUpdate](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/patient.py#15-21), [PatientResponse](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/patient.py#23-34), [PatientListResponse](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/patient.py#36-42) (paginated)
- **[appointment.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/appointment.py)** — [AppointmentCreate](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/appointment.py#7-15), [AppointmentResponse](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/appointment.py#17-28), [AppointmentListResponse](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/appointment.py#30-36)
- **[reminder.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/models/reminder.py)** — [ReminderResponse](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/reminder.py#7-22) (with channel), [ReminderListResponse](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/reminder.py#24-30)
- **[upload.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/upload.py)** — [UploadResponse](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/upload.py#7-12), [UploadDetailResponse](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/upload.py#14-26), [UploadListResponse](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/schemas/upload.py#28-34)
- **[__init__.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/tests/__init__.py)** — Central export of all schemas

---

### 5. Infrastructure Files (3 files updated)

- **[requirements.txt](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/requirements.txt)** — Added `asyncpg`, `passlib[bcrypt]`, `email-validator`
- **[.env.example](file:///c:/Users/sayan/AI%20ML/careremind/.env.example)** — Added `SUPABASE_URL/KEY`, `FAST2SMS_API_KEY`, `CORS_ORIGINS`, `ENVIRONMENT`
- **[main.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/main.py)** — CORS middleware, async lifespan, structured logging, global exception handler, docs disabled in production

---

### 6. Cleanup

- **[middleware/auth.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/middleware/auth.py)** — Converted from empty pass-through to request timing/logging middleware. Auth is now handled per-route via `Depends(get_current_tenant)`.

---

## Design Decisions

| Decision | Why |
|----------|-----|
| **Async SQLAlchemy** | FastAPI is fully async — sync DB calls would block the event loop and kill performance |
| **bcrypt over hashlib** | SHA-256 is not a password hash — it's fast, unsalted, and trivially bruted. bcrypt is the industry standard |
| **Per-route auth** (not middleware) | FastAPI's `Depends()` is more Pythonic, testable, and allows fine-grained control over which routes require auth |
| **Fernet encryption for PII** | Symmetric encryption for phone numbers — allows decryption when needed for sending reminders |
| **JSONB for audit old/new values** | Queryable, indexable, and doesn't require separate encryption management |
| **Date (not DateTime) for visits** | Appointments are date-level — no one books at 3:47 PM at a small clinic |
| **Unique index on (appointment_id, reminder_number)** | Database-level guarantee against duplicate reminders |

---

## What's Next — Phase 2

The foundation is complete. Next session should implement:

1. **Auth API routes** — `POST /api/v1/auth/register` and `POST /api/v1/auth/login`
2. **Patient CRUD routes** — List, create, get patients with phone encryption
3. **Dashboard stats route** — Patient count, reminder counts, upload history
4. **Then test the full loop:** Register → Login → Add Patient → View Patients
