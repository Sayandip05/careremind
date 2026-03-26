# Memory — CareRemind Development Record

## Architecture: Modular Monolith

```
services/
├── fastapi/           # Single FastAPI app (monolith)
│   └── app/
│       ├── features/  # Domain modules (isolated, can extract to microservices)
│       ├── agents/    # AI/LangGraph pipelines
│       ├── core/      # Shared: config, db, security, cache, exceptions
│       ├── middleware/
│       ├── specialty/ # Business logic (7 specialties)
│       └── languages/ # Multilingual support
├── worker/           # Celery background tasks
└── scheduler/        # APScheduler cron jobs
```

---

## Implemented Features (V1)

### Core
- [x] FastAPI with async SQLAlchemy 2.0
- [x] PostgreSQL via Supabase
- [x] JWT authentication (24h expiry)
- [x] Password hashing (bcrypt)
- [x] Phone encryption (Fernet/AES-256)
- [x] Tenant isolation (IDOR protection)
- [x] Multi-language: Hindi, English, Tamil, Marathi, Bengali
- [x] 7 specialties: General, Pediatric, Orthopedic, Eye, Dental, Skin, General

### API Endpoints
- [x] `/api/v1/auth/*` - Register, login, profile
- [x] `/api/v1/patients/*` - CRUD with pagination
- [x] `/api/v1/appointments/*` - List, create
- [x] `/api/v1/reminders/*` - List with status filter
- [x] `/api/v1/upload/excel` - Excel upload
- [x] `/api/v1/upload/photo` - Photo/OCR upload
- [x] `/api/v1/dashboard/stats` - Aggregated stats
- [x] `/api/v1/billing/*` - Payment history, subscription
- [x] `/api/v1/staff/*` - Staff management
- [x] `/api/v1/audit/*` - Activity logs
- [x] `/api/v1/webhooks/whatsapp` - WhatsApp opt-out handling
- [x] `/api/v1/webhooks/whatsapp` - WhatsApp incoming file handling
- [x] `/health`, `/health/ready` - Health checks

### AI Pipeline
- [x] Orchestrator - routes to correct pipeline
- [x] ExcelAgent - parses Excel with flexible columns
- [x] OcrAgent - NVIDIA Gemma 3 vision extraction
- [x] DedupAgent - fuzzy matching on name+phone
- [x] ReminderAgent - creates 7d/30d reminders
- [x] MessageAgent - generates localized messages
- [x] LangGraph state machines for pipelines

### Background Jobs
- [x] Celery worker with task queue
- [x] APScheduler for daily jobs (9AM, 9:30AM, 11AM, midnight)
- [x] Tasks: send reminders, retry failed, daily summary, cleanup

### Infrastructure
- [x] Docker Compose setup
- [x] Nginx reverse proxy
- [x] Redis for queue/cache
- [x] Prometheus + Grafana monitoring
- [x] Sentry SDK integration (configured)
- [x] Async Redis cache client

### Frontend
- [x] React 18 + Vite + TypeScript
- [x] Tailwind CSS + Zustand state
- [x] Dashboard: stats, patients, reminders, upload
- [x] Landing page

### Error Handling
- [x] Global exception handler
- [x] Per-router try/except with logging
- [x] Custom exceptions (NotFound, Conflict, Forbidden)

## System Flow

### V1 (Current) — Doctor Flow

**ONBOARDING (one time)**
1. Doctor visits landing page → clicks Get Started
2. Fills registration: name, clinic name, specialty, WhatsApp number, language preference
3. Adds clinic location(s): clinic_name + address_line + city + pincode (optional, multiple allowed)
4. CareRemind WhatsApp bot number shared with doctor → doctor saves it on phone
5. Setup complete — no more dashboard needed for daily work

**DAILY USAGE (30 seconds/day)**
1. End of clinic day → doctor clicks photo of patient register
2. Sends photo (or Excel) to CareRemind WhatsApp bot
3. Bot processes → replies: "✅ 12 patients added, 3 duplicates skipped"
4. Every 9AM → Celery automatically sends WhatsApp reminders to patients
5. Dashboard is READ-ONLY — doctor checks stats when they want, no daily action needed

**V2 PATIENT BOOKING (closed loop)**
1. Patient receives WhatsApp reminder → "Book your next visit?"
2. If doctor has multiple clinic locations → patient selects which clinic to visit
3. Patient books previous day only (cutoff 11:59 PM) → pays Razorpay → gets bill PDF
4. Online bookings get priority queue (serial 1, 2, 3...)
5. Walk-ins fill reserved slots after online patients
6. Midnight: PDF auto-generated → sent to doctor WhatsApp → handed to receptionist
7. That visit → new appointment record → V1 reminder fires again → loop continues

**CLINIC MANAGEMENT (dashboard)**
- Doctor adds/deletes/updates clinic locations from dashboard
- When doctor moves clinic: delete old entry → add new one
- No complex scheduling per clinic — patient picks clinic during booking (V2)

### ⚠️ GAP FOUND — WhatsApp File Handling Missing!

**Current State:**
- WhatsApp webhook ONLY handles text messages (opt-out)
- Does NOT handle incoming images/documents from WhatsApp
- Doctor uploads via dashboard API, NOT via WhatsApp

**What's Missing:**
- [x] `whatsapp_webhook` now handles `type: image, document`
- [x] Downloads file from Meta → processes like `/upload/photo` or `/upload/excel`
- [x] Routes to appropriate agent (ExcelAgent for document, OcrAgent for image)
- [x] Sends processing result back to doctor via WhatsApp
- [x] Identifies tenant by their registered WhatsApp number

### V2 (Future) — Patient Self-Booking

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Patient   │────▶│   Click     │────▶│   Select    │
│  receives   │     │  reminder   │     │    slot     │
│  reminder   │     │    link     │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                                                │
                                                ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Patient   │◀────│   Confirm  │◀────│   Doctor    │
│   gets      │     │   booking  │     │  notified   │
│  whatsApp   │     │            │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

**V2 Steps:**
1. Patient receives WhatsApp reminder with booking link
2. Patient clicks → opens booking page (no login required)
3. Patient sees doctor's available slots
4. Patient selects slot, enters name + phone
5. Doctor receives notification of new booking
6. Appointment saved → confirmation sent to patient

---

## Issues Fixed (Recent)

| Issue | File | Fix |
|-------|------|-----|
| Middleware not registered | `main.py` | Added TenantContextMiddleware, AuthMiddleware |
| No monitoring | `main.py` | Added Sentry SDK init |
| Sync Redis in async | `core/cache.py` | Changed to `redis.asyncio` |
| Missing error handling | All routers | Added try/except + logging |
| No health check | `main.py` | Added `/health/ready` endpoint |
| WhatsApp file handling missing | `webhooks/router.py` | Now handles image/document uploads |
| get_db return type | `database.py` | Fixed AsyncGenerator type hint |
| UploadLog status type | `upload/models.py` | Changed to String column |

---

## Future Features (V2+)

### Priority 1: Patient Self-Booking
> "same doctor whatsapp patient can book there appointment that logic is different"

**Workflow:**
1. Patient receives WhatsApp reminder with booking link
2. Patient clicks link → opens booking page (no login)
3. Patient sees doctor's available slots
4. Patient selects slot, enters name + phone
5. Doctor receives notification of booking
6. Appointment saved, confirmation sent to patient

**Implementation:**
- New endpoint: `/api/v1/bookings/public` (no auth)
- New table: `booking_slots` (doctor defines available times)
- WhatsApp template with dynamic link
- Webhook to confirm/cancel booking
- Different from tenant's own appointments - owned by patient

**Edge Cases:**
- Slot already taken → show alternatives
- Invalid link/expired → redirect to doctor's booking page
- Doctor disabled booking → show message

### Priority 2: Multi-Tenant SaaS (Coming Soon)
- Subdomains: `clinic.careremind.com`
- Plan tiers: Free, Pro, Enterprise
- Usage limits per plan
- Payment via Razorpay (already configured)

### Priority 3: Advanced Caching
- Redis for dashboard stats (TTL: 5min)
- Patient list caching with invalidation
- Rate limiting per tenant

### Priority 4: Scaling Infrastructure
- Horizontal scaling of FastAPI
- Celery workers with multiple queues
- Read replicas for dashboard
- CDN for static assets

### Priority 5: Additional Features
- [ ] Appointment reminders (not just post-visit)
- [ ] Two-way WhatsApp communication
- [ ] Email notifications
- [ ] Push notifications (PWA)
- [ ] Calendar sync (Google Calendar)
- [ ] Report generation (PDF)
- [ ] Audit log retention policies
- [ ] Tenant admin (manage staff accounts)
- [ ] Two-factor authentication

---

## Technical Debt

### Must Fix
- [x] Fix `get_db` return type warning
- [x] Fix UploadLog status assignment type error
- [ ] Install sentry-sdk (`pip install sentry-sdk`)
- [ ] Test all endpoints after middleware changes

### Should Fix
- [ ] Remove duplicate agent code (old agents vs LangGraph nodes)
- [ ] Add response models to all endpoints
- [ ] Add input sanitization middleware
- [ ] Add rate limiting middleware

### Nice to Have
- [ ] Add OpenAPI security scheme
- [ ] Add API versioning
- [ ] Add request ID for tracing
- [ ] Add structured logging (JSON)

---

## Testing Gaps

### Missing Tests
- [ ] `test_agents.py` - test ExcelAgent, OcrAgent
- [ ] `test_integration.py` - test full upload flow
- [ ] `test_security.py` - test IDOR, encryption

### Existing Tests (Basic)
- [x] test_auth.py
- [x] test_patients.py
- [x] test_reminders.py
- [x] test_upload.py
- [x] test_dashboard.py
- [x] test_health.py

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Modular Monolith | Can extract to microservices later |
| JWT (no refresh) | Simple, 24h sufficient for clinic |
| WhatsApp first | High delivery in India |
| Fernet encryption | Simple, secure for phone numbers |
| LangGraph | Visualizable, testable pipelines |
| APScheduler | Python-native, simple cron |

---

## Notes for Developer

1. **All routes use `Depends(get_current_tenant)`** - returns authenticated Tenant
2. **Queries must filter by `tenant_id`** - prevents IDOR
3. **Phone numbers stored encrypted** - use `encryption_service`
4. **Public paths in AuthMiddleware** - `/health`, `/docs`, `/auth/register`, `/auth/login`, `/webhooks/whatsapp`
5. **Celery tasks are async** - use `_run_async()` wrapper
6. **LangGraph nodes are async** - use `async def`

---

## Last Updated

March 24, 2026
