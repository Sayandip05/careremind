# CareRemind — AI-Powered Patient Reminder System

> Automated WhatsApp and SMS appointment reminders for solo doctors in India.
> Upload a photo or Excel file. AI does everything else.

---

## What is CareRemind?

CareRemind is a production-grade SaaS product built for **solo doctors and small clinics in India**. Doctors upload their patient register — as an Excel file or a phone photo — and the system automatically sends personalized appointment reminders to patients via WhatsApp or SMS.

No manual calling. No missed appointments. No extra work for the doctor.

### Who is this for?

Solo doctors running independent clinics in tier 2 and tier 3 Indian cities who:
- Lose revenue when patients forget follow-up appointments
- Have no existing digital reminder system
- Use WhatsApp daily but are not tech savvy
- Cannot afford or justify enterprise clinic management software

---

## The Problem

Most small Indian clinics have zero patient follow-up system. Staff manually calls patients or nobody follows up at all. This leads to:

- Patients missing follow-up visits and never returning
- Direct revenue loss for the doctor
- Staff time wasted on manual calling
- No record of who was reminded and who was not

CareRemind solves this with one WhatsApp photo per day.

---

## How It Works

```
Doctor or receptionist
clicks photo of patient register
            ↓
Sends photo to CareRemind WhatsApp bot
            ↓
AI reads photo — extracts name, phone, appointment date
            ↓
Deduplication check — skips already existing patients
            ↓
Reminders scheduled based on doctor specialty
            ↓
Patients receive personalized WhatsApp or SMS reminders
            ↓
Doctor receives daily summary report
```

---

## V1 Scope (What Is Built Now)

This is Version 1. It is intentionally focused on the solo doctor use case only.

### Included in V1

- Solo doctor account with JWT authentication
- Excel file upload with automatic patient extraction
- Photo upload with AI-powered OCR text extraction
- Intelligent deduplication — no duplicate reminders ever
- Specialty-aware reminder system (6 specialties)
- Multilanguage reminders — English, Hindi, Bengali, Marathi, Tamil
- WhatsApp reminders via Meta Cloud API
- SMS fallback via Fast2SMS for patients without WhatsApp
- Automatic channel detection — WhatsApp first, SMS fallback
- Daily scheduler — reminders sent automatically every morning
- Retry engine — failed reminders retried automatically
- Doctor dashboard — upload, view patients, view reminder status
- Daily summary report sent to doctor on WhatsApp
- Anti-spam rules — no duplicate sends, opt-out handling
- HIPAA-style encryption — patient phone numbers encrypted at rest
- Audit logging — every action logged with timestamp
- Background job processing — Celery + Redis queue
- Docker containerization — all services
- CI/CD pipeline — GitHub Actions

### Not in V1 (Planned for V2 and V3)

- Receptionist staff accounts and access management
- Multi-doctor clinic support
- Razorpay subscription billing (manual billing for now)
- Grafana monitoring dashboards
- Sentry error tracking
- Kubernetes deployment

---

## Tech Stack

### Backend
| Service | Technology | Purpose |
|---------|------------|---------|
| FastAPI | Python 3.11 | AI processing, async API, agents |
| Django | Python 3.11 | Admin panel, auth management |
| Celery | Python | Background job processing |
| APScheduler | Python | Scheduled daily reminder jobs |
| WhatsApp Service | Node.js | Meta Cloud API integration |

### Database and Infrastructure
| Component | Technology | Purpose |
|-----------|------------|---------|
| Database | PostgreSQL via Supabase | Primary data store |
| Cache + Queue | Redis | Job queue and caching |
| File Storage | Supabase Storage | Excel and photo uploads |
| Hosting | Render (free tier) | Backend services |
| Frontend | Vercel (free tier) | Dashboard and landing page |

### AI and External Services
| Service | Purpose | AWS Migration Path |
|---------|---------|-------------------|
| Groq (Llama 3) | Message generation | OpenAI (config change) |
| Google Vision | Photo OCR | AWS Textract (config change) |
| Meta Cloud API | WhatsApp sending | No migration needed |
| Fast2SMS | SMS fallback | Twilio (config change) |

### Frontend
| App | Technology | URL |
|-----|------------|-----|
| Doctor Dashboard | React + Vite + Tailwind | app.careremind.in |
| Landing Page | Next.js + Tailwind | careremind.in |

---

## High Level Design (HLD)

The CareRemind architecture is designed to handle asynchronous tasks (like AI OCR and Excel parsing) separately from fast API requests, ensuring the mobile-friendly dashboard remains responsive.

```mermaid
graph TD
    %% Actors
    Doc[Doctor / Receptionist]
    Patient[Patient]

    %% Frontends
    subgraph Frontend CDN
        Land[Landing Page]
        Dash[Doctor Dashboard]
    end

    %% Backend Services
    subgraph Backend Services
        API[FastAPI Backend]
        Worker[Celery Worker]
        Cron[APScheduler Jobs]
        Admin[Django Admin]
    end

    %% Storage & Queue
    subgraph Infrastructure
        PG[(PostgreSQL)]
        Redis[(Redis Queue/Cache)]
        Store[Supabase Storage]
    end

    %% External APIs
    subgraph External APIs
        Groq[Groq Llama 3]
        Vision[Google Vision OCR]
        Meta[WhatsApp Cloud API]
        SMS[Fast2SMS]
    end

    %% Connections - Frontend
    Doc -->|Logs in, Uploads Data| Dash
    Land -->|Redirects to| Dash
    Dash <-->|REST API| API
    Admin <-->|Direct DB Access| PG

    %% Connections - Core Logic
    API <-->|Reads/Writes| PG
    API -->|Enqueues Tasks| Redis
    Redis -->|Consumes Tasks| Worker
    Cron -->|Triggers Daily Reminders| Redis

    %% Connections - Storage
    API -->|Uploads Excel/Photo| Store
    Worker -->|Downloads for Processing| Store

    %% Connections - AI
    Worker <-->|Generates Messages| Groq
    Worker <-->|Extracts Text from Photos| Vision

    %% Connections - Delivery
    Worker -->|Sends Reminders| Meta
    Worker -->|Fallback SMS| SMS
    Meta -->|Delivers| Patient
    SMS -->|Delivers| Patient

    %% Webhooks
    Meta -->|Delivery Status & Replies| API
```

---

## Project Structure

```
careremind/
│
├── services/
│   ├── fastapi/                    # AI engine and async API
│   │   └── app/
│   │       ├── api/v1/             # All API endpoints
│   │       ├── agents/             # AI agent system
│   │       ├── specialty/          # Specialty reminder strategies
│   │       ├── languages/          # Multilanguage handlers
│   │       ├── core/               # Config, DB, security
│   │       ├── middleware/         # Auth, rate limiting, audit
│   │       ├── models/             # SQLAlchemy database models
│   │       ├── schemas/            # Pydantic request/response schemas
│   │       ├── services/           # Business logic layer
│   │       └── utils/              # Phone formatter, date parser
│   │
│   ├── django/                     # Admin panel and auth
│   │   ├── careremind_admin/       # Django project settings
│   │   └── apps/
│   │       ├── accounts/           # Doctor authentication
│   │       ├── tenants/            # Tenant management
│   │       └── audit/              # Audit log viewer
│   │
│   ├── worker/                     # Celery background jobs
│   │   └── tasks/
│   │       ├── excel_tasks.py      # Excel processing
│   │       ├── ocr_tasks.py        # Photo OCR processing
│   │       ├── reminder_tasks.py   # Reminder sending
│   │       └── cleanup_tasks.py    # Maintenance jobs
│   │
│   ├── scheduler/                  # Reminder scheduler
│   │   └── jobs/
│   │       ├── daily_reminder_job.py    # 9AM — send today's reminders
│   │       ├── summary_report_job.py    # 9:30AM — doctor summary
│   │       └── retry_failed_job.py      # 11AM — retry failures
│   │
│   └── whatsapp/                   # Node.js WhatsApp service
│       └── src/
│           ├── sender.js           # Meta Cloud API sends
│           ├── receiver.js         # Incoming message handler
│           ├── optout_handler.js   # STOP reply handling
│           └── rate_limiter.js     # Max 20 messages per minute
│
├── frontend/
│   ├── landing/                    # Next.js marketing website
│   └── dashboard/                  # React doctor dashboard
│       └── src/
│           ├── pages/              # Login, Dashboard, Upload, Patients, Reminders
│           ├── components/         # Reusable UI components
│           ├── hooks/              # Custom React hooks
│           ├── store/              # Zustand state management
│           └── api/                # Axios API clients
│
├── infrastructure/
│   ├── nginx/                      # Reverse proxy config
│   ├── terraform/                  # AWS IaC (ready, not active)
│   └── kubernetes/                 # K8s manifests (future)
│
├── monitoring/
│   ├── prometheus/                 # Metrics collection
│   └── grafana/                    # Dashboards (V2)
│
├── .github/workflows/
│   ├── ci.yml                      # Lint, test, type check on every push
│   ├── cd-staging.yml              # Deploy to staging on develop branch
│   └── cd-production.yml           # Deploy to production on main branch
│
├── docker-compose.yml              # Local development — all services
├── docker-compose.prod.yml         # Production configuration
├── Makefile                        # Developer shortcuts
└── README.md
```

---

## Database Schema

```sql
-- Row Level Security enabled on all tables
-- Every table filtered by tenant_id

tenants
  id, doctor_name, clinic_name, email,
  specialty, language_preference,
  whatsapp_number, plan,
  trial_ends_at, is_active, created_at

patients
  id, tenant_id, name,
  phone_encrypted,              -- AES-256 encrypted at rest
  preferred_channel,            -- whatsapp | sms | both
  has_whatsapp,                 -- auto detected
  language_preference,          -- per patient override
  is_optout, created_at

appointments
  id, tenant_id, patient_id,
  visit_date, next_visit_date,
  specialty_override,           -- per visit specialty override
  notes_encrypted,
  source,                       -- excel | photo | manual
  created_at

reminders
  id, tenant_id, appointment_id,
  reminder_number,              -- 1 or 2
  status,                       -- Pending | Sent | Failed | Confirmed | Cancelled | Optout
  message_text, language_used,
  channel,                      -- whatsapp | sms
  scheduled_at, sent_at, error_log

upload_logs
  id, tenant_id, filename, file_type,
  total_rows, duplicates_skipped,
  failed_rows, status, created_at

audit_logs
  id, tenant_id, user_id,
  action, resource, resource_id,
  ip_address, created_at        -- append only, never deleted
```

---

## AI Agent System

The system uses multiple specialized agents coordinated by a master orchestrator.

| Agent | File | Purpose |
|-------|------|---------|
| Orchestrator | `orchestrator.py` | Decides which agent runs for each task |
| Excel Agent | `excel_agent.py` | Reads and validates Excel uploads |
| OCR Agent | `ocr_agent.py` | Extracts text from prescription photos |
| Reminder Agent | `reminder_agent.py` | Applies specialty reminder strategy |
| Message Agent | `message_agent.py` | Generates multilanguage messages via Groq |
| Dedup Agent | `dedup_agent.py` | Identifies and skips duplicate patients |
| Report Agent | `report_agent.py` | Generates daily doctor summary |

### Specialty Reminder Strategies

Each medical specialty has its own timing and message strategy.

| Specialty | Reminder Timing | Message Focus |
|-----------|----------------|---------------|
| Dermatology | 3 days + 1 day before | Avoid sun exposure, skincare prep |
| Dental | 2 days + 2 hours before | Don't eat before, bring X-rays |
| Pediatric | 2 days + 1 day before | Gentle tone, addressed to parent |
| Orthopedic | 3 days + 1 day before | Bring MRI and X-ray reports |
| Eye Clinic | 1 day + 3 hours before | Arrange transport, vision check |
| General | 2 days + morning of | Bring previous reports |

### Adding a New Specialty

```python
# services/fastapi/app/specialty/cardiology.py
from app.specialty.base_specialty import BaseSpecialty

class CardiologySpecialty(BaseSpecialty):
    def get_reminder_timing(self) -> list[int]:
        return [7, 3, 1]  # days before appointment

    def get_message_template(self) -> str:
        return "Your cardiology appointment is on {date}. Please bring your ECG reports."

    def get_tone(self) -> str:
        return "professional"
```

### Language Support

| Language | Code | Greeting |
|----------|------|---------|
| English | en | Hello |
| Hindi | hi | नमस्ते |
| Bengali | bn | নমস্কার |
| Marathi | mr | नमस्कार |
| Tamil | ta | வணக்கம் |

---

## Anti-Spam System

Proper WhatsApp usage requires strict anti-spam controls. CareRemind enforces:

- One reminder per appointment per reminder slot — database status check before every send
- Sending window — messages only sent between 9AM and 7PM IST
- Meta approved templates — all messages use pre-approved WhatsApp templates
- Opt-out handling — patient replies STOP, number blacklisted immediately and permanently
- Rate limiting — maximum 20 messages per minute per WhatsApp number
- Reminder timing — sent 2-3 days before, not same day morning
- Confirmation handling — patient replies YES, marked Confirmed, no further messages

---

## Notification Channel Logic

```
Patient record created
        ↓
Has WhatsApp? (auto detected via Meta API)
        ↓
YES → Send via WhatsApp (Meta Cloud API)
        ↓
NO or WhatsApp delivery failed?
        ↓
Fallback → Send via SMS (Fast2SMS)
        ↓
Both failed → Log as Failed
Doctor sees failure on dashboard
```

---

## Security Architecture

| Layer | What It Does |
|-------|-------------|
| Network | Nginx reverse proxy, HTTPS only, CORS whitelist |
| Authentication | JWT tokens, 24 hour expiry, role embedded in token |
| Authorization | RBAC — doctor has full access to own tenant only |
| Multi-tenancy | tenant_id on every query + Supabase Row Level Security |
| Encryption | AES-256 for patient phone numbers and notes at rest |
| Audit logging | Every create/update/delete logged, append-only |
| Input validation | Pydantic on all inputs, phone normalization, file type limits |

---

## AWS Migration Path

This project is built free-first but AWS-ready. Every service has a direct AWS equivalent requiring only a config change — no code rewrite.

| Current (Free) | AWS Equivalent | Config Change |
|----------------|----------------|---------------|
| Supabase Storage | AWS S3 | `STORAGE_BACKEND=s3` |
| Google Vision | AWS Textract | `VISION_BACKEND=textract` |
| Supabase PostgreSQL | AWS RDS | `DATABASE_URL=...rds...` |
| Redis on Render | AWS ElastiCache | `REDIS_URL=...elasticache...` |
| Render hosting | AWS ECS | Use existing Dockerfiles |
| Env key encryption | AWS KMS | One line change in `encryption_service.py` |

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+
- Python 3.11+

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd careremind

# Copy environment variables
cp .env.example .env
# Fill in required values in .env

# Start all services
make dev

# Run database migrations
make migrate
```

### Local Service URLs

| Service | URL |
|---------|-----|
| Doctor Dashboard | http://localhost:3000 |
| Landing Page | http://localhost:3002 |
| FastAPI Docs | http://localhost:8000/docs |
| Django Admin | http://localhost:8001/admin |

---

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

All endpoints require: `Authorization: Bearer <jwt_token>`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload/excel` | Upload Excel file with patient data |
| POST | `/upload/photo` | Upload photo for OCR extraction |
| GET | `/patients` | List all patients for tenant |
| POST | `/patients` | Create single patient manually |
| GET | `/reminders` | List all reminders with status |
| POST | `/reminders/trigger/{id}` | Manually trigger a reminder |
| GET | `/dashboard/stats` | Dashboard statistics |
| POST | `/webhooks/whatsapp` | Incoming WhatsApp webhook |
| GET | `/health` | Health check |

---

## Environment Variables

```bash
# .env.example — copy to .env and fill in values

# Database
DATABASE_URL=postgresql://user:password@host:5432/careremind

# Cache and Queue
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET_KEY=your-secret-key-minimum-32-chars
JWT_EXPIRY_HOURS=24

# Patient Data Encryption
FIELD_ENCRYPTION_KEY=your-256-bit-encryption-key

# AI — Message Generation
GROQ_API_KEY=your-groq-api-key

# WhatsApp
META_WHATSAPP_TOKEN=your-meta-token
META_PHONE_NUMBER_ID=your-phone-number-id

# SMS Fallback
FAST2SMS_API_KEY=your-fast2sms-key

# Vision OCR
VISION_BACKEND=google
GOOGLE_VISION_KEY=your-google-vision-key

# Storage
STORAGE_BACKEND=local

# AWS (leave empty until migration)
AWS_S3_BUCKET=
AWS_ACCESS_KEY=
AWS_SECRET_KEY=
AWS_TEXTRACT_REGION=

# Monitoring (leave empty for now)
SENTRY_DSN=
```

---

## CI/CD Pipeline

```
Push to any branch
        ↓
ci.yml — Python linting (ruff), type checking (mypy),
         pytest, Django tests, TypeScript check, Docker build test
        ↓
Push to develop branch
        ↓
cd-staging.yml — Build images, push to GitHub Container Registry,
                 deploy to Render staging, run smoke tests
        ↓
Push to main branch (requires manual approval)
        ↓
cd-production.yml — Build production images,
                    run database migrations,
                    deploy to Render production
```

---

## Makefile Commands

```bash
make dev        # Start all services locally
make test       # Run all tests
make migrate    # Run database migrations
make build      # Build all Docker images
make logs       # Tail all service logs
make shell      # Open FastAPI Python shell
make admin      # Open Django admin shell
make clean      # Stop and remove all containers
```

---

## Roadmap

### V1 — Solo Doctor (Current)
Excel upload, photo OCR, WhatsApp + SMS reminders, specialty system, multilanguage, dashboard, audit logs, Docker, CI/CD.

### V2 — Add Receptionist
Receptionist staff accounts with limited access. Doctor invites receptionist via email. Receptionist can upload and view only.

### V3 — Multi-Doctor Clinic
Multiple doctors under one clinic account. Owner doctor manages billing. Each doctor sees only their own patients.

### V4 — Scale
Razorpay subscription billing automated. Kubernetes deployment. Full Grafana monitoring. AWS migration.

---

## License

Private — All rights reserved. This is a commercial product.

---

## Contact

For technical issues or questions contact via WhatsApp only.