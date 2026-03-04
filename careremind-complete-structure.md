# CareRemind — Enterprise Grade Full Product Structure
## AWS-Ready | Multi-Tenant | Agentic AI | Full Security

---

## Philosophy of This Architecture

- Free now. AWS swap = config change only. No code rewrite ever.
- FastAPI handles all AI, async, WhatsApp, agents, file processing
- Django handles admin panel, auth management, user management, billing
- Both share the same PostgreSQL database via Supabase
- Every feature is a separate module. Add or remove without breaking anything.
- Security is not an afterthought. It is baked into every layer.

---

## Complete Monorepo Structure

```
careremind/
│
├── 📁 services/
│   ├── 📁 fastapi/                        # AI, Async, Agents, WhatsApp
│   ├── 📁 django/                         # Auth, Admin, Billing, Management
│   ├── 📁 worker/                         # Celery background jobs
│   ├── 📁 scheduler/                      # APScheduler reminder engine
│   └── 📁 whatsapp/                       # Node.js WhatsApp service
│
├── 📁 frontend/
│   ├── 📁 landing/                        # Next.js landing page
│   └── 📁 dashboard/                      # React + Vite doctor dashboard
│
├── 📁 infrastructure/
│   ├── 📁 docker/                         # All Dockerfiles
│   ├── 📁 nginx/                          # Reverse proxy config
│   ├── 📁 terraform/                      # AWS IaC (ready but not active)
│   └── 📁 kubernetes/                     # K8s manifests (future scaling)
│
├── 📁 monitoring/
│   ├── 📁 prometheus/                     # Metrics collection
│   ├── 📁 grafana/                        # Dashboards
│   └── 📁 sentry/                         # Error tracking config
│
├── 📁 .github/
│   └── 📁 workflows/                      # CI/CD pipelines
│
├── docker-compose.yml                     # Local development
├── docker-compose.prod.yml                # Production
├── docker-compose.monitoring.yml          # Monitoring stack
├── Makefile                               # Dev shortcuts
└── README.md
```

---

## Service 1 — FastAPI (AI Engine + Async API)

```
services/fastapi/
│
├── 📁 app/
│   │
│   ├── 📁 api/
│   │   └── 📁 v1/
│   │       ├── __init__.py
│   │       ├── router.py                  # Registers all route groups
│   │       ├── upload.py                  # Excel + photo upload endpoints
│   │       ├── reminders.py               # Reminder CRUD + trigger
│   │       ├── patients.py                # Patient management
│   │       ├── dashboard.py               # Stats and analytics
│   │       ├── webhooks.py                # WhatsApp + Razorpay webhooks
│   │       ├── health.py                  # Health check endpoint
│   │       └── agent.py                   # Agent interaction endpoints
│   │
│   ├── 📁 agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py                # Master agent — decides which agent runs
│   │   ├── excel_agent.py                 # Processes Excel uploads
│   │   ├── ocr_agent.py                   # Processes photo uploads
│   │   ├── reminder_agent.py              # Decides reminder logic per specialty
│   │   ├── message_agent.py               # Generates messages per language
│   │   ├── dedup_agent.py                 # Deduplication intelligence
│   │   └── report_agent.py                # Generates doctor summary reports
│   │
│   ├── 📁 specialty/
│   │   │   # THIS IS YOUR AGENTIC REMINDER SYSTEM
│   │   │   # Each specialty has its own reminder strategy
│   │   ├── __init__.py
│   │   ├── base_specialty.py              # Abstract base class
│   │   ├── skin.py                        # Dermatology reminders
│   │   ├── diagnosis.py                   # General diagnosis reminders
│   │   ├── dental.py                      # Dental reminders
│   │   ├── pediatric.py                   # Child clinic reminders
│   │   ├── orthopedic.py                  # Bone and joint reminders
│   │   ├── eye.py                         # Eye clinic reminders
│   │   └── general.py                     # Default fallback
│   │
│   ├── 📁 languages/
│   │   │   # MULTILANGUAGE REMINDER SYSTEM
│   │   ├── __init__.py
│   │   ├── base_language.py               # Abstract language handler
│   │   ├── english.py
│   │   ├── hindi.py
│   │   ├── bengali.py
│   │   ├── marathi.py
│   │   ├── tamil.py
│   │   └── detector.py                    # Auto detects patient language from name/region
│   │
│   ├── 📁 core/
│   │   ├── __init__.py
│   │   ├── config.py                      # All settings from environment
│   │   ├── database.py                    # Supabase + SQLAlchemy connection
│   │   ├── storage.py                     # File storage (local now, S3 swap ready)
│   │   ├── cache.py                       # Redis cache client
│   │   ├── queue.py                       # Celery queue client
│   │   ├── security.py                    # Encryption, hashing utilities
│   │   └── exceptions.py                  # Custom exception handlers
│   │
│   ├── 📁 middleware/
│   │   ├── __init__.py
│   │   ├── auth.py                        # JWT verification middleware
│   │   ├── rate_limiter.py                # Per tenant rate limiting
│   │   ├── audit_logger.py                # Every action logged
│   │   ├── tenant_context.py              # Injects tenant_id into every request
│   │   └── input_sanitizer.py             # Cleans all incoming data
│   │
│   ├── 📁 models/
│   │   ├── __init__.py
│   │   ├── tenant.py                      # Doctor/clinic account
│   │   ├── patient.py                     # Patient record
│   │   ├── appointment.py                 # Visit and next visit
│   │   ├── reminder.py                    # Reminder record + status
│   │   ├── upload_log.py                  # File upload history
│   │   ├── audit_log.py                   # Security audit trail
│   │   ├── staff.py                       # Receptionist accounts
│   │   └── message_template.py            # Approved WhatsApp templates
│   │
│   ├── 📁 schemas/
│   │   ├── __init__.py
│   │   ├── tenant.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   ├── reminder.py
│   │   └── upload.py
│   │
│   ├── 📁 services/
│   │   ├── __init__.py
│   │   ├── whatsapp_service.py            # Meta Cloud API integration
│   │   ├── groq_service.py                # Groq LLM calls
│   │   ├── vision_service.py              # Google Vision (S3+Textract swap ready)
│   │   ├── encryption_service.py          # HIPAA-style field encryption
│   │   ├── notification_service.py        # Orchestrates full reminder pipeline
│   │   └── tenant_service.py              # Tenant lifecycle management
│   │
│   ├── 📁 utils/
│   │   ├── __init__.py
│   │   ├── phone_formatter.py             # Normalize all phone numbers to +91
│   │   ├── date_parser.py                 # Handle DD/MM/YYYY, DD-MM-YYYY etc
│   │   ├── excel_validator.py             # Validate uploaded Excel format
│   │   └── language_detector.py          # Detect language from name/region
│   │
│   └── main.py                            # FastAPI app entry point
│
├── 📁 tests/
│   ├── 📁 unit/
│   │   ├── test_agents.py
│   │   ├── test_deduplication.py
│   │   ├── test_specialty.py
│   │   └── test_languages.py
│   ├── 📁 integration/
│   │   ├── test_upload_flow.py
│   │   ├── test_reminder_flow.py
│   │   └── test_webhook_flow.py
│   └── conftest.py
│
├── 📁 alembic/                            # DB migrations
│   ├── versions/
│   └── env.py
│
├── .env.example
├── requirements.txt
├── Dockerfile
└── alembic.ini
```

---

## Service 2 — Django (Admin + Auth + Billing)

```
services/django/
│
├── 📁 careremind_admin/                   # Django project folder
│   ├── settings/
│   │   ├── base.py                        # Shared settings
│   │   ├── development.py                 # Dev overrides
│   │   └── production.py                  # Prod overrides
│   ├── urls.py
│   └── wsgi.py
│
├── 📁 apps/
│   │
│   ├── 📁 accounts/                       # Doctor and staff auth
│   │   ├── models.py                      # CustomUser extending AbstractUser
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── admin.py                       # Django admin registration
│   │   └── urls.py
│   │
│   ├── 📁 tenants/                        # Multi tenant management
│   │   ├── models.py                      # Tenant model
│   │   ├── admin.py                       # Superadmin can see all tenants
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── 📁 billing/                        # Razorpay subscription management
│   │   ├── models.py                      # Payment, subscription models
│   │   ├── razorpay_client.py             # Razorpay API wrapper
│   │   ├── views.py                       # Payment endpoints
│   │   ├── webhooks.py                    # Razorpay webhook handler
│   │   └── admin.py
│   │
│   ├── 📁 staff/                          # Receptionist management
│   │   ├── models.py                      # Staff model with role
│   │   ├── permissions.py                 # RBAC — doctor vs receptionist
│   │   ├── views.py
│   │   └── admin.py
│   │
│   └── 📁 audit/                          # Audit log viewer in admin
│       ├── models.py
│       ├── admin.py
│       └── views.py
│
├── 📁 tests/
├── manage.py
├── requirements.txt
└── Dockerfile
```

---

## Service 3 — Celery Worker (Background Jobs)

```
services/worker/
│
├── 📁 tasks/
│   ├── __init__.py
│   ├── excel_tasks.py                     # Process uploaded Excel files
│   ├── ocr_tasks.py                       # Process uploaded photos
│   ├── reminder_tasks.py                  # Send individual reminders
│   ├── report_tasks.py                    # Generate doctor reports
│   └── cleanup_tasks.py                   # Delete old files, expired data
│
├── celery_app.py                          # Celery configuration
├── requirements.txt
└── Dockerfile
```

---

## Service 4 — Scheduler (Reminder Engine)

```
services/scheduler/
│
├── jobs/
│   ├── __init__.py
│   ├── daily_reminder_job.py              # Runs 9AM — finds tomorrow's appointments
│   ├── summary_report_job.py              # Runs 9:30AM — sends doctor summary
│   ├── retry_failed_job.py                # Runs 11AM — retries failed reminders
│   └── cleanup_job.py                     # Runs midnight — cleanup tasks
│
├── scheduler.py                           # APScheduler setup
├── requirements.txt
└── Dockerfile
```

---

## Service 5 — WhatsApp Service (Node.js)

```
services/whatsapp/
│
├── src/
│   ├── index.js                           # Express server entry point
│   ├── sender.js                          # Send message via Meta Cloud API
│   ├── receiver.js                        # Receive incoming WhatsApp messages
│   ├── template_manager.js                # Manage approved Meta templates
│   ├── optout_handler.js                  # Handle STOP replies immediately
│   └── rate_limiter.js                    # Max 20 messages per minute
│
├── package.json
└── Dockerfile
```

---

## Frontend 1 — Landing Page (Next.js)

```
frontend/landing/
│
├── 📁 app/
│   ├── page.tsx                           # Main landing page
│   ├── pricing/page.tsx                   # Pricing page
│   ├── layout.tsx
│   └── globals.css
│
├── 📁 components/
│   ├── Hero.tsx
│   ├── Problem.tsx
│   ├── HowItWorks.tsx
│   ├── Features.tsx
│   ├── Pricing.tsx
│   ├── Testimonials.tsx
│   ├── FinalCTA.tsx
│   ├── Navbar.tsx
│   └── Footer.tsx
│
├── 📁 lib/
│   └── razorpay.ts                        # Razorpay checkout integration
│
├── next.config.js
├── tailwind.config.js
├── package.json
└── Dockerfile
```

---

## Frontend 2 — Doctor Dashboard (React + Vite)

```
frontend/dashboard/
│
├── 📁 src/
│   ├── 📁 pages/
│   │   ├── Login.tsx
│   │   ├── Onboarding.tsx                 # First time setup wizard
│   │   ├── Dashboard.tsx                  # Stats overview
│   │   ├── Upload.tsx                     # Excel + photo upload
│   │   ├── Patients.tsx                   # Patient list
│   │   ├── Reminders.tsx                  # Reminder history + status
│   │   ├── Staff.tsx                      # Add receptionist accounts
│   │   ├── Settings.tsx                   # Clinic settings + specialty
│   │   └── Billing.tsx                    # Subscription management
│   │
│   ├── 📁 components/
│   │   ├── StatsCard.tsx
│   │   ├── PatientTable.tsx
│   │   ├── ReminderTimeline.tsx
│   │   ├── UploadZone.tsx                 # Drag drop with progress
│   │   ├── AgentStatus.tsx                # Live AI processing updates
│   │   ├── SpecialtySelector.tsx          # Doctor selects their specialty
│   │   ├── LanguageSelector.tsx           # Default reminder language
│   │   └── RoleGuard.tsx                  # Shows UI based on role
│   │
│   ├── 📁 hooks/
│   │   ├── useAuth.ts
│   │   ├── usePatients.ts
│   │   ├── useReminders.ts
│   │   └── useUpload.ts
│   │
│   ├── 📁 store/
│   │   ├── authStore.ts                   # Zustand auth state
│   │   └── tenantStore.ts                 # Current tenant context
│   │
│   ├── 📁 api/
│   │   ├── client.ts                      # Axios instance with JWT
│   │   ├── patients.ts
│   │   ├── reminders.ts
│   │   └── upload.ts
│   │
│   └── App.tsx
│
├── vite.config.ts
├── tailwind.config.js
├── package.json
└── Dockerfile
```

---

## Database Schema (Supabase PostgreSQL)

```sql
-- Every table has tenant_id for multi-tenancy
-- Row Level Security enabled on every table

tenants
  id, clinic_name, email, specialty,        -- specialty decides reminder strategy
  language_preference, whatsapp_number,
  plan, trial_ends_at, is_active, created_at

staff
  id, tenant_id, name, email,
  role (doctor | receptionist | admin),
  is_active, created_at

patients
  id, tenant_id, name,
  phone_encrypted,                           -- HIPAA encrypted at rest
  language_preference,                       -- per patient language override
  is_optout, created_at

appointments
  id, tenant_id, patient_id,
  visit_date, next_visit_date,
  specialty_override,                        -- override clinic specialty per visit
  notes_encrypted, source (excel|photo|manual),
  created_by_role, created_at

reminders
  id, tenant_id, appointment_id,
  reminder_number (1 or 2),
  status (Pending|Sent|Failed|Confirmed|Cancelled|Optout),
  message_text, language_used,
  scheduled_at, sent_at, error_log

message_templates
  id, tenant_id, specialty, language,
  template_name, meta_template_id,          -- Meta approved template ID
  body, is_active

upload_logs
  id, tenant_id, filename, file_type,
  total_rows, duplicates_skipped,
  failed_rows, status, s3_url, created_at

audit_logs
  id, tenant_id, user_id, role,
  action, resource, resource_id,
  ip_address, user_agent,
  old_value_encrypted, new_value_encrypted,
  created_at

payments
  id, tenant_id, razorpay_order_id,
  razorpay_payment_id, amount,
  plan, status, created_at
```

---

## Security Architecture

```
Layer 1 — Network
  Nginx reverse proxy — all traffic through single entry point
  Rate limiting at nginx level — 100 requests per minute per IP
  HTTPS only — HTTP redirects to HTTPS automatically
  CORS whitelist — only your frontend domains allowed

Layer 2 — Authentication
  Django issues JWT tokens on login
  FastAPI verifies JWT on every request via middleware
  Token expiry 24 hours. Refresh token 30 days.
  Role embedded in JWT — doctor | receptionist | superadmin

Layer 3 — Authorization (RBAC)
  Doctor    — full access to own tenant data
  Receptionist — upload, view patients, view reminders only
              — cannot see billing, cannot delete, cannot change settings
  Superadmin — Django admin panel only — sees all tenants

Layer 4 — Multi Tenancy
  tenant_id injected into every request via middleware
  Every database query automatically filtered by tenant_id
  Supabase Row Level Security as second enforcement layer
  Even if code bug — RLS prevents cross tenant data leak

Layer 5 — Data Encryption
  Patient phone numbers encrypted at rest using AES-256
  Appointment notes encrypted at rest
  Encryption key stored in environment variable
  AWS KMS ready — swap env key for KMS call = one line change

Layer 6 — Audit Logging
  Every create, update, delete logged with user, role, timestamp
  Old and new values stored encrypted
  Audit logs are append only — nobody can delete them
  Viewable only by superadmin in Django admin panel

Layer 7 — Input Validation
  Pydantic validates every incoming request in FastAPI
  Phone numbers normalized and validated
  Dates parsed strictly — invalid dates rejected
  File uploads scanned for type — only xlsx, jpg, png accepted
  File size limit 10MB enforced
```

---

## Agentic Reminder System — How It Works

```
Doctor sets specialty during onboarding
Example: Dermatology (Skin)
        ↓
Patient uploaded with next visit date
        ↓
reminder_agent.py checks doctor specialty
Loads skin.py specialty handler
        ↓
skin.py defines:
  - Reminder timing: 3 days before + 1 day before
  - Message tone: friendly, mention skin care tips
  - Template: "Your skin checkup is on {date}.
    Remember to avoid sun exposure 24 hours before visit."
        ↓
message_agent.py generates message
Checks patient language preference
If Hindi → generates Hindi message via Groq
If Bengali → generates Bengali message via Groq
If no preference → uses clinic default language
        ↓
WhatsApp service sends approved template
Patient receives personalized specialty-aware
language-aware reminder automatically
```

---

## Specialty Reminder Strategy Breakdown

```
Skin (Dermatology)
  Timing     — 3 days before, 1 day before
  Message    — Mention sun exposure, skincare prep
  Follow up  — 7 days after visit for follow-up check

General Diagnosis
  Timing     — 2 days before, morning of appointment
  Message    — Bring previous reports and prescriptions
  Follow up  — Based on doctor notes

Dental
  Timing     — 2 days before, 2 hours before
  Message    — Don't eat 2 hours before, bring X-rays
  Follow up  — 6 month routine reminder

Pediatric
  Timing     — 2 days before, 1 day before
  Message    — Gentle tone, addressed to parent
  Follow up  — Vaccination schedule reminders

Orthopedic
  Timing     — 3 days before, 1 day before
  Message    — Bring MRI/X-ray reports
  Follow up  — Physiotherapy session reminders

Eye Clinic
  Timing     — 1 day before, 3 hours before
  Message    — Arrange transport, vision may be blurred after
  Follow up  — Annual checkup reminder
```

---

## Storage Architecture (AWS Ready)

```
Now (Free)                    Later (AWS — config change only)
─────────────────────         ──────────────────────────────
Supabase Storage         →    AWS S3
  uploaded Excel files         same files, same code
  uploaded photos              just change STORAGE_BACKEND=s3
  generated reports            in .env file

Google Vision API        →    AWS Textract
  photo OCR                    same interface
  free 1000/month              change VISION_BACKEND=textract

Render PostgreSQL        →    AWS RDS
  database                     change DATABASE_URL in .env

Redis on Render          →    AWS ElastiCache
  job queue + cache            change REDIS_URL in .env

Render hosting           →    AWS ECS or EC2
  all services                 use existing Dockerfiles
```

---

## CI/CD Pipeline (GitHub Actions)

```
.github/workflows/

ci.yml — runs on every push to any branch
  ├── Python linting (ruff)
  ├── Type checking (mypy)
  ├── Run FastAPI tests (pytest)
  ├── Run Django tests
  ├── Frontend type check (tsc)
  └── Docker build test (ensure images build)

cd-staging.yml — runs on push to develop branch
  ├── Build all Docker images
  ├── Push to GitHub Container Registry (free)
  ├── Deploy to Render staging environment
  └── Run smoke tests on staging URL

cd-production.yml — runs on push to main branch
  ├── Requires CI to pass first
  ├── Requires manual approval (GitHub environments)
  ├── Build production Docker images
  ├── Deploy to Render production
  ├── Run database migrations automatically
  └── Notify on Slack or email if deploy fails
```

---

## Docker Compose — Full Local Setup

```yaml
# All services run locally with one command
# docker-compose up

Services:
  nginx          — port 80, reverse proxy to all services
  fastapi        — port 8000, AI and async API
  django         — port 8001, admin and auth
  worker         — Celery worker, no port
  scheduler      — APScheduler, no port
  whatsapp       — port 3001, WhatsApp service
  dashboard      — port 3000, React frontend
  landing        — port 3002, Next.js landing
  postgres       — port 5432, local database
  redis          — port 6379, queue and cache
  prometheus     — port 9090, metrics
  grafana        — port 3003, dashboards
```

---

## Monitoring Stack

```
Prometheus — collects metrics from FastAPI and Django
  - Request count per endpoint
  - Response time per endpoint
  - Error rate per tenant
  - Reminder success rate
  - Queue depth (how many jobs waiting)

Grafana — visualizes Prometheus metrics
  - Real time dashboard
  - Alert when error rate exceeds 5%
  - Alert when queue depth exceeds 100 jobs
  - Daily reminder success rate chart

Sentry — error tracking
  - Every Python exception captured with full stack trace
  - Every failed reminder logged with reason
  - Alert on new error types immediately

All three run free locally via Docker
Grafana Cloud free tier for production monitoring
Sentry free tier for production error tracking
```

---

## Environment Variables Structure

```
# .env.example — commit this
# .env — never commit this

# Database
DATABASE_URL=postgresql://...           # Supabase → AWS RDS: change this only

# Storage
STORAGE_BACKEND=local                   # local | s3
AWS_S3_BUCKET=                          # empty until AWS migration
AWS_ACCESS_KEY=
AWS_SECRET_KEY=

# Vision OCR
VISION_BACKEND=google                   # google | textract
GOOGLE_VISION_KEY=
AWS_TEXTRACT_REGION=                    # empty until AWS migration

# AI
GROQ_API_KEY=
OPENAI_API_KEY=                         # empty until added

# WhatsApp
META_WHATSAPP_TOKEN=
META_PHONE_NUMBER_ID=

# Auth
JWT_SECRET_KEY=
JWT_EXPIRY_HOURS=24

# Encryption
FIELD_ENCRYPTION_KEY=                   # AES-256 key for patient data

# Payments
RAZORPAY_KEY_ID=
RAZORPAY_SECRET=

# Cache
REDIS_URL=redis://redis:6379

# Monitoring
SENTRY_DSN=
```

---

## Makefile — Developer Shortcuts

```makefile
make dev          # Start all services locally
make test         # Run all tests
make migrate      # Run database migrations
make shell        # Open FastAPI shell
make admin        # Open Django admin shell
make logs         # Tail all service logs
make build        # Build all Docker images
make clean        # Stop and remove all containers
```

---

## How Staff (Receptionist) Feature Works

```
Doctor signs up → creates tenant
Doctor goes to Staff page in dashboard
Doctor adds receptionist email and name
System sends invite email to receptionist
Receptionist sets password via invite link
        ↓
Receptionist logs in — sees limited dashboard
Can access: Upload page, Patient list view
Cannot access: Billing, Settings, Staff management,
              Delete any records, View audit logs
        ↓
All receptionist actions logged in audit_logs
Doctor can revoke access anytime
Multiple receptionists per clinic supported
```

---

## Summary — What Makes This Enterprise Grade

```
Multi-tenancy        Row Level Security — zero cross tenant leakage
Security             6 layer security from network to database
HIPAA-style          Phone and notes encrypted at rest
Audit logs           Every action traceable forever
RBAC                 Doctor, receptionist, superadmin roles
Agentic AI           Specialty-aware reminder strategy
Multilanguage        Hindi, Bengali, English, Marathi, Tamil
Background jobs      Celery + Redis — no request timeouts ever
Monitoring           Prometheus + Grafana + Sentry
CI/CD                Automated test, build, deploy pipeline
AWS Ready            Every free service has AWS swap in config only
Docker               Every service containerized identically
Scalable             Add more Celery workers = handle 10x load
```

---

## Build Order (What to Build First)

```
Week 1    FastAPI skeleton + database models + JWT auth
Week 2    Excel upload + deduplication + Groq messages
Week 3    Celery worker + Redis queue + background processing
Week 4    WhatsApp Meta Cloud API + anti spam rules
Week 5    Specialty system + multilanguage system
Week 6    Django admin + billing + staff management
Week 7    React dashboard + all pages connected to API
Week 8    Next.js landing page + Razorpay checkout
Week 9    Monitoring setup + CI/CD pipeline
Week 10   Full end to end testing + first real doctor onboarding
```
