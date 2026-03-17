# CareRemind V1 — What's Already Implemented

> **Target User:** Solo doctor running a private clinic  
> **One doctor → One login → One dashboard → Their patients → Their reminders**

---

## 1. HTTP & How the Web Works ✅
- FastAPI serves all HTTP requests (GET, POST, PATCH, DELETE)
- Async request handling with `uvicorn` ASGI server
- CORS middleware configured for frontend origins
- Request/response lifecycle managed via middleware stack

## 2. Routing & Path Operations ✅
- **14 route modules** under `/api/v1/`:
  - `auth` — register, login, profile
  - `patients` — CRUD with pagination
  - `appointments` — list, create
  - `reminders` — list with status filtering
  - `upload` — Excel and photo upload endpoints
  - `dashboard` — aggregated stats in single DB query
  - `billing` — payment history, subscription status
  - `audit` — activity log viewer
  - `staff` — staff member management
  - `webhooks` — WhatsApp opt-out handling
  - `health` — load balancer health check
  - `agent` — AI agent status

## 3. JSON & Data Serialization ✅
- Pydantic v2 schemas for all request/response models
- `model_validate()` for ORM → JSON conversion
- Proper datetime serialization with timezone awareness
- `from_attributes = True` for SQLAlchemy model integration

## 4. Authentication & Authorization ✅
- **Registration:** `POST /auth/register` — bcrypt password hashing via `passlib`
- **Login:** `POST /auth/login` — returns signed JWT (24h expiry)
- **Token verification:** `python-jose` JWT decode with expiry check
- **Auth dependency:** `get_current_tenant` injects the authenticated doctor into every protected route
- **IDOR protection:** All queries filter by `tenant_id` — a doctor can only see their own data

## 5. Data Validation (Pydantic) ✅
- **Request schemas:** `TenantRegister`, `TenantLogin`, `PatientCreate`, `PatientUpdate`
- **Response schemas:** `TenantResponse`, `PatientResponse`, `PatientListResponse`, `ReminderResponse`, `ReminderListResponse`
- Field constraints: `min_length`, `max_length`, `EmailStr`, `Field(ge=1, le=100)` for pagination
- Enums: `PlanType`, `ReminderStatus`, `UploadStatus`, `StaffRole`, `PreferredChannel`

## 6. Application Architecture ✅
```
app/
├── api/v1/        → Route handlers (thin controllers)
├── services/      → Business logic (auth, patient, notification, tenant)
├── agents/        → AI pipeline (orchestrator, excel, ocr, dedup, reminder, message)
├── models/        → SQLAlchemy ORM models (8 tables)
├── schemas/       → Pydantic validation schemas
├── core/          → Config, database, security, storage, exceptions
├── specialty/     → Specialty-specific reminder timing rules (7 specialties)
├── languages/     → Multilingual message templates (5 languages)
├── middleware/     → Request processing middleware
└── utils/         → Shared utilities
```

## 7. API Design Best Practices ✅
- RESTful URL structure (`/patients`, `/patients/{id}`)
- API versioning (`/api/v1/`)
- Pagination on all list endpoints (`page`, `per_page` params)
- Consistent JSON error responses with `detail` field
- HTTP status codes: 200, 201, 400, 401, 404, 500
- Health check endpoint for monitoring

## 8. Databases & ORMs (SQLAlchemy) ✅
- **Async SQLAlchemy 2.0** with `asyncpg` driver
- **Supabase PostgreSQL** as the database
- **8 models:** Tenant, Patient, Appointment, Reminder, UploadLog, AuditLog, Staff, Payment
- Connection pooling: `pool_size=5`, `max_overflow=10`, `pool_pre_ping=True`
- Relationships with cascading deletes
- `async_session` alias for worker/scheduler tasks

## 9. Caching (Redis) ⚠️ Partial
- Redis configured as **Celery message broker** (task queue)
- Redis URL from environment variable
- **NOT YET:** API-level response caching (dashboard stats, patient lists)

## 10. Task Queues (Celery) ✅
- **5 task modules:**
  - `reminder_tasks` — send pending reminders, retry failed ones
  - `excel_tasks` — background Excel processing
  - `ocr_tasks` — background photo/OCR processing
  - `report_tasks` — daily summary to doctor via WhatsApp
  - `cleanup_tasks` — delete old uploads (30d) and reminders (90d)
- IST timezone, `acks_late` for crash recovery, soft/hard time limits

## 11. Error Handling ✅
- Global exception handler in `main.py` (hides internals in production)
- Custom `HTTPException` with proper status codes in all routes
- File validation errors (wrong format, too large)
- Duplicate detection errors (duplicate patient phone)
- Auth errors (invalid credentials, expired token)

## 12. Configuration Management ✅
- `pydantic-settings` with `BaseSettings` class
- `.env` file loading with `python-dotenv`
- Environment-specific behavior (dev vs production)
- Secrets: `JWT_SECRET_KEY`, `FIELD_ENCRYPTION_KEY`, API keys
- Configurable: DB pool size, CORS origins, JWT expiry

## 14. Graceful Shutdown & Lifespan ✅
- FastAPI `lifespan` context manager for startup/shutdown logging
- Celery `acks_late` ensures unfinished tasks are re-queued on crash
- APScheduler `misfire_grace_time` handles scheduler downtime

## 15. Backend Security ✅
- **PII encryption:** `cryptography.Fernet` AES-256 for patient phone numbers
- **Password hashing:** bcrypt via passlib
- **JWT tokens** with expiry
- **IDOR protection:** tenant-scoped queries on every endpoint
- **CORS** configured per environment
- **WhatsApp opt-out** webhook handling

## 22. Webhooks ✅
- `POST /api/v1/webhooks/whatsapp` — receives WhatsApp messages
- Detects opt-out keywords (STOP, unsubscribe, etc.)
- Marks patient as opted out, cancels pending reminders
- Webhook verification for Meta Cloud API

## 25. API Documentation (OpenAPI) ✅
- FastAPI auto-generates Swagger UI at `/docs`
- ReDoc at `/redoc`
- Disabled in production (`docs_url=None`)
- All endpoints have docstrings and response model annotations

## 26. 12-Factor App ✅
- Config from environment variables (not hardcoded)
- Stateless processes (no in-memory state between requests)
- Port binding via uvicorn
- Backing services (Postgres, Redis) attached via URLs
- Dev/prod parity via Docker
- Logs to stdout

## 27. Docker & Docker Compose ✅
- `docker-compose.yml` with 8 services: FastAPI, Worker, Scheduler, Dashboard, Landing, Postgres, Redis, Nginx
- Individual Dockerfiles per service
- Shared `.env` file
- Volume mounts for development
- Monitoring stack: Prometheus + Grafana (compose override)

---

## AI Pipeline (Unique Selling Point) ✅
- **Orchestrator Agent** — routes upload to correct pipeline
- **Excel Agent** — parses `.xlsx` with flexible column mapping
- **OCR Agent** — NVIDIA Gemma 3 vision API extracts patient data from register photos
- **Dedup Agent** — fuzzy matching on name + phone to prevent duplicates
- **Reminder Agent** — creates reminders at 7 days and 30 days after visit
- **Message Agent** — generates multilingual messages (5 languages) with optional GPT polish
- **Notification Service** — WhatsApp (Meta Cloud API) primary, SMS (Fast2SMS) fallback

## Frontend ✅
- **Landing Page** — Vite + React marketing site at `frontend/landing/`
- **Doctor Dashboard** — Vite + React 18 + TypeScript + Tailwind + Zustand
  - Login/Register page
  - Dashboard with 6 stat cards
  - Upload (drag-and-drop Excel/Photo)
  - Patients (paginated table)
  - Reminders (status-filtered list)

## Background Jobs (APScheduler) ✅
- 9:00 AM IST — Send pending reminders
- 9:30 AM IST — Daily summary to doctor
- 11:00 AM IST — Retry failed reminders
- 12:00 AM IST — Cleanup old records
