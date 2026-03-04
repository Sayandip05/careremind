# CareRemind — AI-Powered Healthcare Reminder System

---

## Table of Contents

1. [What is CareRemind?](#what-is-careremind)
2. [The Problem We Solve](#the-problem-we-solve)
3. [How It Works](#how-it-works)
4. [Key Features](#key-features)
5. [Architecture Overview](#architecture-overview)
6. [Tech Stack](#tech-stack)
7. [Project Structure](#project-structure)
8. [Getting Started](#getting-started)
9. [API Endpoints](#api-endpoints)
10. [Database Schema](#database-schema)
11. [Security](#security)
12. [Multitenancy](#multitenancy)
13. [Agent System](#agent-system)
14. [WhatsApp Integration](#whatsapp-integration)
15. [Development Guide](#development-guide)
16. [Environment Variables](#environment-variables)

---

## What is CareRemind?

**CareRemind** is an enterprise-grade healthcare reminder system designed for clinics and doctors to automatically send appointment reminders to patients via WhatsApp. It uses AI to personalize reminders based on the doctor's specialty (dermatology, dental, pediatric, etc.) and supports multiple languages (English, Hindi, Bengali, Marathi, Tamil).

### Product Vision
- **Free now, AWS-ready later** — Built with free services (Supabase, Render) but designed to swap to AWS with only config changes, no code rewrites
- **Multi-tenant** — Multiple doctors/clinics can use the same system with complete data isolation
- **Agentic AI** — Specialty-aware reminder strategies that adapt to different medical fields
- **HIPAA-style security** — Patient phone numbers and notes encrypted at rest

---

## The Problem We Solve

### For Doctors/Clinics
1. **No-Show Patients** — Patients forget appointments, leading to lost revenue and inefficient schedules
2. **Manual Reminders** — Staff spends hours calling each patient individually
3. **Language Barriers** — Need to send reminders in patient's preferred language
4. **Specialty-Specific Needs** - Different medical specialties require different reminder timing and content (dental vs skin checkups)
5. **Staff Management** - Receptionists need limited access without seeing sensitive billing data

### For Patients
1. **Missed Appointments** - Forget scheduled visits, especially for follow-ups
2. **Language Accessibility** - Receive reminders in their native language
3. **Opt-Out Convenience** - Can easily reply "STOP" to opt out

---

## How It Works

### The Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Doctor    │────▶│   Upload    │────▶│     AI      │────▶│  WhatsApp   │
│   Uploads   │     │   Excel/    │     │   Processes │     │   Sends     │
│   Patients  │     │   Photo     │     │   & Schedules│    │   Reminder  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Step-by-Step Process

1. **Doctor uploads patient data** via Excel file or photo of appointment book
2. **AI Agent processes the data**:
   - Extracts patient names, phone numbers, next visit dates
   - Deduplicates existing patients
   - Detects language from patient name/region
3. **Reminder Agent decides**:
   - When to send (3 days before, 1 day before, etc.)
   - What message to send based on doctor's specialty
4. **Message Agent generates** the personalized message in the patient's language
5. **WhatsApp service sends** the reminder via Meta Cloud API
6. **Patient can reply** "STOP" to opt out

### Specialty-Aware Reminders

| Specialty | Timing | Message Focus |
|-----------|--------|---------------|
| Dermatology (Skin) | 3 days + 1 day before | Sun exposure warnings, skincare prep |
| Dental | 2 days + 2 hours before | Don't eat before, bring X-rays |
| Pediatric | 2 days + 1 day before | Gentle tone to parent |
| Orthopedic | 3 days + 1 day before | Bring MRI/X-ray reports |
| Eye Clinic | 1 day + 3 hours before | Arrange transport |
| General Diagnosis | 2 days + morning of | Bring previous reports |

---

## Key Features

### Core Features
- [x] Excel/CSV patient upload with deduplication
- [x] Photo upload with OCR text extraction
- [x] Automatic appointment date parsing
- [x] WhatsApp message sending via Meta Cloud API
- [x] Multi-language support (EN, HI, BN, MR, TA)
- [x] Specialty-aware reminder strategies
- [x] Opt-out handling (STOP replies)
- [x] Rate limiting (max 20 msgs/minute)
- [x] Retry failed reminders
- [x] Daily summary reports for doctors

### Security Features
- [x] JWT-based authentication
- [x] Role-based access control (Doctor, Receptionist, Admin)
- [x] AES-256 field encryption for sensitive data
- [x] Audit logging of all actions
- [x] Row-level security in database
- [x] Tenant isolation

### Enterprise Features
- [x] Multi-tenant architecture
- [x] Staff/receptionist management
- [x] Subscription/billing (Razorpay integration ready)
- [x] Webhook handlers (WhatsApp, Razorpay)
- [x] Prometheus metrics collection
- [x] Grafana dashboards
- [x] Sentry error tracking

---

## Architecture Overview

### System Design

```
                                    ┌──────────────────┐
                                    │      Nginx       │
                                    │  (Reverse Proxy)│
                                    └────────┬─────────┘
                                             │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
            ┌───────▼────────┐        ┌───────▼────────┐        ┌───────▼────────┐
            │    FastAPI    │        │     Django     │        │   WhatsApp     │
            │  (AI & Async) │        │ (Admin & Auth) │        │    Service     │
            └───────┬────────┘        └───────┬────────┘        └───────┬────────┘
                    │                         │                         │
                    └─────────────────────────┼─────────────────────────┘
                                              │
                                    ┌─────────▼─────────┐
                                    │   PostgreSQL       │
                                    │   (Supabase)       │
                                    └─────────┬─────────┘
                                    ┌─────────▼─────────┐
                                    │      Redis        │
                                    │ (Cache + Queue)   │
                                    └──────────────────┘
                                              │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
            ┌───────▼────────┐        ┌───────▼────────┐        ┌───────▼────────┐
            │    Celery      │        │   APScheduler  │        │   Frontend     │
            │    Worker      │        │   (Scheduler)  │        │   (React)      │
            └────────────────┘        └────────────────┘        └────────────────┘
```

### Services

| Service | Port | Technology | Purpose |
|---------|------|------------|---------|
| FastAPI | 8000 | Python | AI processing, async API |
| Django | 8001 | Python | Admin panel, auth, billing |
| Worker | - | Python/Celery | Background job processing |
| Scheduler | - | Python/APScheduler | Scheduled reminder jobs |
| WhatsApp | 3001 | Node.js | Meta Cloud API integration |
| Dashboard | 3000 | React/Vite | Doctor dashboard UI |
| Landing | 3002 | Next.js | Marketing landing page |

---

## Tech Stack

### Backend
- **FastAPI** — Modern Python async web framework
- **Django** — Full-featured Python web framework for admin
- **SQLAlchemy** — Python ORM
- **Celery** — Distributed task queue
- **APScheduler** — Job scheduling

### Database & Cache
- **PostgreSQL** — Primary database (via Supabase)
- **Redis** — Cache and message broker

### Frontend
- **React** — UI library (Dashboard)
- **Next.js** — React framework (Landing page)
- **Vite** — Build tool
- **Tailwind CSS** — Styling
- **Zustand** — State management
- **Axios** — HTTP client

### External Services
- **Meta Cloud API** — WhatsApp messaging
- **Groq** — LLM for message generation
- **Google Vision** — OCR for photo uploads
- **Razorpay** — Payment processing (ready)

### Infrastructure
- **Docker** — Containerization
- **GitHub Actions** — CI/CD
- **Prometheus** — Metrics
- **Grafana** — Monitoring dashboards

---

## Project Structure

```
careremind/
│
├── services/                    # Backend microservices
│   ├── fastapi/                # AI & async API
│   │   ├── app/
│   │   │   ├── api/v1/        # API endpoints
│   │   │   ├── agents/        # AI agents
│   │   │   ├── specialty/     # Specialty strategies
│   │   │   ├── languages/     # Language handlers
│   │   │   ├── core/          # Config, DB, security
│   │   │   ├── middleware/    # Auth, rate limiting
│   │   │   ├── models/        # SQLAlchemy models
│   │   │   ├── schemas/       # Pydantic schemas
│   │   │   ├── services/      # Business logic
│   │   │   └── utils/         # Helpers
│   │   ├── tests/
│   │   └── alembic/           # DB migrations
│   │
│   ├── django/                 # Admin & Auth
│   │   ├── careremind_admin/  # Django project
│   │   │   └── settings/      # Settings configs
│   │   ├── apps/              # Django apps
│   │   │   ├── accounts/      # User auth
│   │   │   ├── tenants/       # Tenant management
│   │   │   ├── billing/       # Payments
│   │   │   ├── staff/         # Staff management
│   │   │   └── audit/         # Audit logs
│   │   └── manage.py
│   │
│   ├── worker/                 # Celery worker
│   │   ├── tasks/
│   │   │   ├── excel_tasks.py
│   │   │   ├── ocr_tasks.py
│   │   │   ├── reminder_tasks.py
│   │   │   └── cleanup_tasks.py
│   │   └── celery_app.py
│   │
│   ├── scheduler/              # APScheduler jobs
│   │   ├── jobs/
│   │   │   ├── daily_reminder_job.py
│   │   │   └── summary_report_job.py
│   │   └── scheduler.py
│   │
│   └── whatsapp/              # Node.js WhatsApp service
│       └── src/
│           ├── sender.js       # Send messages
│           ├── receiver.js    # Receive messages
│           └── rate_limiter.js
│
├── frontend/                   # Frontend applications
│   ├── landing/               # Next.js landing page
│   │   ├── app/              # Next.js app router
│   │   ├── components/       # UI components
│   │   └── lib/             # Utilities
│   │
│   └── dashboard/             # React dashboard
│       ├── src/
│       │   ├── pages/       # Page components
│       │   ├── components/   # Reusable components
│       │   ├── hooks/        # Custom React hooks
│       │   ├── store/        # Zustand stores
│       │   └── api/          # API clients
│       └── vite.config.ts
│
├── infrastructure/            # DevOps & Infrastructure
│   ├── docker/               # Dockerfiles
│   ├── nginx/                # Nginx configs
│   ├── terraform/            # AWS IaC
│   └── kubernetes/           # K8s manifests
│
├── monitoring/               # Observability
│   ├── prometheus/           # Metrics config
│   ├── grafana/              # Dashboards
│   └── sentry/               # Error tracking
│
├── .github/workflows/        # CI/CD pipelines
│   ├── ci.yml               # Lint, test, type check
│   ├── cd-staging.yml       # Deploy to staging
│   └── cd-production.yml    # Deploy to production
│
├── docker-compose.yml        # Local development
├── docker-compose.prod.yml   # Production
├── docker-compose.monitoring.yml
├── Makefile                 # Developer shortcuts
└── README.md                # This file
```

---

## Getting Started

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Node.js** 18+ (for frontend development)
- **Python** 3.11+ (for local development)
- **Git** for version control

### Quick Start (Docker)

```bash
# Clone the repository
git clone <repository-url>
cd careremind

# Copy environment variables
cp .env.example .env

# Start all services
make dev

# Or manually with docker-compose
docker-compose up
```

### Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| Dashboard | http://localhost:3000 | Doctor dashboard |
| Landing | http://localhost:3002 | Marketing page |
| FastAPI | http://localhost:8000 | API docs |
| Django Admin | http://localhost:8001/admin | Admin panel |
| WhatsApp API | http://localhost:3001 | WhatsApp service |

### Local Development Without Docker

```bash
# FastAPI
cd services/fastapi
pip install -r requirements.txt
uvicorn app.main:app --reload

# Django
cd services/django
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001

# Frontend
cd frontend/dashboard
npm install
npm run dev

# WhatsApp Service
cd services/whatsapp
npm install
npm start
```

---

## API Endpoints

### FastAPI Base URL: `http://localhost:8000/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload/excel` | Upload Excel file with patients |
| POST | `/upload/photo` | Upload photo for OCR |
| GET | `/patients` |
| POST | `/patients` | List all patients | Create new patient |
| GET | `/reminders` | List reminders |
| POST | `/reminders/tr}` | Trigger reminderigger/{id manually |
| GET | `/dashboard/stats` | Get dashboard statistics |
| POST | `/webhooks/whatsapp` | WhatsApp webhook |
| POST | `/webhooks/razorpay` | Razorpay webhook |
| GET | `/health` | Health check |

### Authentication

All endpoints require JWT token in header:
```
Authorization: Bearer <token>
```

---

## Database Schema

### Core Tables

```sql
-- Tenants (Clinics/Doctors)
tenants (
    id, clinic_name, email, specialty,
    language_preference, whatsapp_number,
    plan, is_active, created_at
)

-- Staff (Users)
staff (
    id, tenant_id, name, email,
    role (doctor/receptionist/admin),
    is_active, created_at
)

-- Patients
patients (
    id, tenant_id, name,
    phone_encrypted, language_preference,
    is_optout, created_at
)

-- Appointments
appointments (
    id, tenant_id, patient_id,
    visit_date, next_visit_date,
    specialty_override, notes_encrypted,
    source (excel/photo/manual), created_at
)

-- Reminders
reminders (
    id, tenant_id, appointment_id,
    reminder_number (1/2),
    status (Pending/Sent/Failed/Confirmed/Cancelled/Optout),
    message_text, language_used,
    scheduled_at, sent_at, error_log
)

-- Message Templates
message_templates (
    id, tenant_id, specialty, language,
    template_name, meta_template_id,
    body, is_active
)

-- Upload Logs
upload_logs (
    id, tenant_id, filename, file_type,
    total_rows, duplicates_skipped,
    failed_rows, status, created_at
)

-- Audit Logs
audit_logs (
    id, tenant_id, user_id, role,
    action, resource, resource_id,
    ip_address, user_agent, created_at
)
```

---

## Security

### Layer 1: Network
- Nginx reverse proxy
- Rate limiting (100 requests/minute/IP)
- HTTPS only
- CORS whitelist

### Layer 2: Authentication
- JWT tokens with 24-hour expiry
- Role embedded in token

### Layer 3: Authorization (RBAC)
- **Doctor**: Full access to own tenant
- **Receptionist**: Upload, view patients/reminders only
- **Superadmin**: All tenants via Django admin

### Layer 4: Multi-Tenancy
- tenant_id in every request header
- Automatic filtering of all queries
- Supabase Row Level Security (RLS)

### Layer 5: Data Encryption
- AES-256 encryption for phone numbers and notes
- Encryption key in environment variable
- AWS KMS ready (swap config)

### Layer 6: Audit Logging
- Every create/update/delete logged
- User, role, IP, timestamp captured
- Append-only (cannot be deleted)

### Layer 7: Input Validation
- Pydantic validation on all inputs
- Phone number normalization
- Strict date parsing
- File type and size limits

---

## Multitenancy

### How It Works

1. Each doctor/clinic is a **Tenant**
2. Each tenant has a unique `tenant_id`
3. Every API request must include `X-Tenant-ID` header
4. All database queries automatically filter by tenant_id
5. Staff accounts belong to a specific tenant

### Tenant Isolation

```python
# Example: Middleware injects tenant_id
def get_patients(tenant_id: str):
    return db.query(Patient).filter(Patient.tenant_id == tenant_id).all()
```

### Switching Between Tenants

```bash
# Include tenant ID in requests
curl -H "X-Tenant-ID: clinic_123" http://localhost:8000/api/v1/patients
```

---

## Agent System

### AI Agents

The system uses multiple specialized agents:

| Agent | Purpose |
|-------|---------|
| **Orchestrator** | Decides which agent to run |
| **ExcelAgent** | Processes patient Excel uploads |
| **OcrAgent** | Extracts text from photos |
| **ReminderAgent** | Determines reminder timing/content per specialty |
| **MessageAgent** | Generates messages in patient's language |
| **DedupAgent** | Identifies duplicate patients |
| **ReportAgent** | Creates daily summary reports |

### Specialty Strategies

Each medical specialty has its own reminder strategy:

```python
# Example: Dermatology (Skin)
skin.py:
    - Timing: 3 days before, 1 day before
    - Message: "Remember to avoid sun exposure 24 hours before"
    - Tone: Friendly

# Example: Dental
dental.py:
    - Timing: 2 days before, 2 hours before  
    - Message: "Don't eat 2 hours before, bring X-rays"
    - Tone: Caring
```

### Language Support

| Language | Code | Greeting |
|----------|------|----------|
| English | en | Hello |
| Hindi | hi | नमस्ते |
| Bengali | bn | নমস্কার |
| Marathi | mr | नमस्कार |
| Tamil | ta | வணக்கம் |

---

## WhatsApp Integration

### Meta Cloud API

- Uses WhatsApp Business API via Meta
- Pre-approved message templates required
- Rate limit: 20 messages/minute
- Webhook for incoming messages

### Opt-Out Handling

Patients can reply:
- "STOP" — Opt out of all reminders
- "UNSTOP" — Re-subscribe

### Message Flow

```python
# 1. Doctor creates appointment
# 2. ReminderAgent schedules reminders
# 3. At scheduled time, Worker sends to WhatsApp service
# 4. WhatsApp service calls Meta API
# 5. Message delivered to patient
```

---

## Development Guide

### Adding a New Specialty

1. Create new file in `services/fastapi/app/specialty/`
2. Extend `BaseSpecialty` class
3. Define reminder timing and message template
4. Register in the specialty factory

```python
# services/fastapi/app/specialty/cardiology.py
from app.specialty.base_specialty import BaseSpecialty

class CardiologySpecialty(BaseSpecialty):
    def get_reminder_timing(self):
        return [7, 3, 1]  # 7 days, 3 days, 1 day before
    
    def get_message_template(self):
        return "Your cardiology appointment is on {date}. Bring ECG reports."
    
    def get_tone(self):
        return "professional"
```

### Adding a New Language

1. Create new file in `services/fastapi/app/languages/`
2. Extend `BaseLanguage` class
3. Implement format_date() and get_greeting()

### Adding a New API Endpoint

1. Create or modify file in `services/fastapi/app/api/v1/`
2. Define Pydantic schemas in `services/fastapi/app/schemas/`
3. Register route in `services/fastapi/app/api/v1/router.py`

### Adding a New Frontend Page

1. Create component in `frontend/dashboard/src/pages/`
2. Add route in `frontend/dashboard/src/App.tsx`
3. Create API client in `frontend/dashboard/src/api/`

---

## Environment Variables

### Required Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/careremind

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_EXPIRY_HOURS=24

# Encryption
FIELD_ENCRYPTION_KEY=your-256-bit-key

# Groq (LLM)
GROQ_API_KEY=your-groq-key

# WhatsApp
META_WHATSAPP_TOKEN=your-token
META_PHONE_NUMBER_ID=your-phone-id
```

### Optional Variables

```bash
# Storage (default: local)
STORAGE_BACKEND=local  # or s3

# Vision OCR (default: google)
VISION_BACKEND=google  # or textract

# Payments
RAZORPAY_KEY_ID=your-key
RAZORPAY_SECRET=your-secret

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

---

## Common Tasks

### Run Tests
```bash
make test
```

### Run Migrations
```bash
make migrate
```

### View Logs
```bash
make logs
```

### Rebuild Containers
```bash
make build
```

### Clean Up
```bash
make clean
```

### Open FastAPI Shell
```bash
make shell
```

### Open Django Shell
```bash
make admin
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

### Code Quality

- Python: Use `ruff` for linting
- TypeScript: Use `eslint` and `prettier`
- Run lint before commit:
  ```bash
  # Python
  ruff check services/fastapi/
  
  # TypeScript
  npm run lint
  ```

---

## License

Private — All rights reserved

---

## Support

For issues and questions:
- Report bugs via GitHub Issues
- Check architecture docs in `careremind-complete-structure.md`

---

## Roadmap

See `careremind-complete-structure.md` for detailed 10-week build plan:

- Week 1-2: FastAPI skeleton + auth
- Week 3-4: Excel upload + WhatsApp
- Week 5-6: Specialty system + Django admin
- Week 7-8: React dashboard + landing page
- Week 9-10: Monitoring + CI/CD + testing
