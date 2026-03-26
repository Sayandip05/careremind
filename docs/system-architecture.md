# System Architecture

## Overview

CareRemind is a **Modular Monolith** - a single deployable FastAPI application with isolated domain modules. Background jobs run via Celery and APScheduler.

```
┌─────────────────────────────────────────────────────────────┐
│                     Nginx (Reverse Proxy)                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│Dashboard │ │ Landing  │ │  FastAPI │
│  (3000)  │ │  (3002)  │ │  (8000)  │
└──────────┘ └──────────┘ └────┬─────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
  ┌────────────┐        ┌────────────┐        ┌────────────┐
  │  Postgres  │        │   Redis    │        │  Supabase  │
  │  (Database)│        │ (Queue/Cache)       │  (Storage) │
  └────────────┘        └────────────┘        └────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │  Worker  │ │Scheduler │ │   AI     │
              │ (Celery) │ │(APSched) │ │(GroQ/Vision)│
              └──────────┘ └──────────┘ └──────────┘
```

---

## Architecture Patterns

### 1. Modular Monolith

```
services/fastapi/app/
├── features/          # Domain modules (isolated)
│   ├── auth/         # Authentication + Tenant profile
│   ├── clinics/      # ClinicLocation CRUD (multi-clinic support)
│   ├── patients/     # Patient CRUD
│   ├── appointments/ # Visit records
│   ├── reminders/    # Reminder scheduling + notification
│   ├── upload/       # Excel/photo upload (dashboard path)
│   ├── billing/      # Payment history + subscription
│   ├── staff/        # Staff management
│   ├── audit/        # Activity logs
│   ├── dashboard/    # Aggregated stats (read-only)
│   └── webhooks/     # WhatsApp incoming (PRIMARY upload path + opt-out)
├── agents/          # AI pipelines
├── core/            # Shared infrastructure + integrations
├── middleware/      # Cross-cutting concerns
├── specialty/       # Business logic (7 specialties)
└── utils/           # Helpers
```

**Rules:**
- Features don't import each other's routers or services
- Features can import other features' models (FK lookups)
- All features use `core/` for DB, security, config, integrations
- `webhooks/` is the PRIMARY daily upload path (WhatsApp bot)
- `upload/` is the SECONDARY path (dashboard, optional)

### 2. Event-Driven Background Jobs

```
Upload → Extract → Deduplicate → Save → Create Reminders → Send
              │           │          │         │            │
              ▼           ▼          ▼         ▼            ▼
         LangGraph    Agent      DB      Scheduler    Celery
```

### 3. Multi-Tenant with Row-Level Security

- Every query filters by `tenant_id`
- Patient phone numbers encrypted at rest
- IDOR protection on all endpoints

---

## Tech Stack Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| API | FastAPI | Async, automatic docs, type safety |
| ORM | SQLAlchemy 2.0 | Async support, type-safe queries |
| Auth | JWT + bcrypt | Stateless, industry standard |
| Queue | Celery + Redis | Mature, easy debugging |
| Scheduler | APScheduler | Python-native cron |
| AI | LangGraph | State machine for pipelines |
| Vision | NVIDIA Gemma 3 / GPT-4o Mini | Best cost/quality |
| WhatsApp | Meta Cloud API | Reliable in India |
| SMS | Fast2SMS | Fallback |

---

## Data Flow

### Upload Flow — WhatsApp Bot (Primary, Daily)
```
1. Doctor sends photo/Excel to CareRemind WhatsApp bot
2. Webhook receives file from Meta API
3. FastAPI identifies tenant by sender's WhatsApp number
4. OcrAgent (photo) or ExcelAgent (Excel) extracts rows
5. DedupAgent checks duplicates
6. Saves new patients + appointments to DB
7. ReminderAgent creates reminders (7d, 30d)
8. Bot replies to doctor: "✅ 12 added, 3 skipped"
```

### Upload Flow — Dashboard (Secondary/Optional)
```
1. Doctor/staff uploads Excel/photo from dashboard
2. FastAPI saves to Supabase Storage
3. ExcelAgent/OcrAgent extracts rows
4. DedupAgent checks duplicates
5. Saves new patients + appointments
6. ReminderAgent creates reminders (7d, 30d)
7. Dashboard shows result summary
```

### Reminder Flow
```
1. Scheduler triggers at 9:00 AM IST
2. Celery task queries pending reminders
3. For each reminder:
   a. MessageAgent generates localized message
   b. NotificationService sends via WhatsApp
   c. On failure → retry with SMS fallback
4. Update status in DB
```

---

## ADR Summary

| ADR | Decision | Rationale |
|-----|----------|-----------|
| Async DB | asyncpg driver | Non-blocking I/O for high concurrency |
| Modular Monolith | Single FastAPI app | Simpler than microservices, can extract later |
| JWT Auth | No refresh tokens | 24h expiry sufficient for clinic use |
| Phone Encryption | Fernet (AES-256) | Simple, secure for PII |
| WhatsApp First | Meta Cloud API | High delivery in India |
| LangGraph | State machines for pipelines | Visualizable, testable |

---

## Scaling Path

**Current (V1):**
- Single FastAPI instance
- 1 Worker + 1 Scheduler
- Single PostgreSQL

**Future (V2):**
- FastAPI behind load balancer (multiple instances)
- Celery workers scaled horizontally
- Read replicas for dashboard queries
- Redis cluster for caching

**Long-term (V3):**
- Extract features to microservices
- Event bus (Kafka) for async communication
- Kubernetes with HPA
