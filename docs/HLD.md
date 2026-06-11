# High-Level Design (HLD) & System Architecture - CareRemind

**Version**: 1.1  
**Last Updated**: 2026-06-11  
**Status**: Production-Ready  
**Document Type**: Unified Architecture Design & High-Level Design

---

## 1. Executive Summary & Problem Statement

Indian clinics struggle with patient no-shows and manual reminder management. Doctors spend hours calling patients to remind them of appointments, leading to:
- **High no-show rates** (30-40% in small clinics)
- **Wasted doctor time** on manual calls
- **Lost revenue** from missed appointments
- **Poor patient experience** due to forgotten appointments

**CareRemind** is a production-grade, AI-powered, multi-tenant SaaS platform that automates appointment reminders via WhatsApp (Meta Cloud API). It supports online patient bookings, payment processing, multiple clinic locations, automated daily schedule compilation (PDF), and a web dashboard for doctors, helping them streamline their clinic operations.

---

## 2. Who is the User & What Pain It Solves

### Primary User
**Individual doctors** in India (general practitioners, dentists, pediatricians, dermatologists, eye specialists, orthopedics, etc.) who run their own clinics and manage appointments.

### Pain Points Solved
- ✅ **Automated Reminders**: No more manual phone calls or text messages.
- ✅ **WhatsApp-First Delivery**: Personalized notifications sent directly to WhatsApp (the most active communication channel in India).
- ✅ **Intelligent Specialty Scheduling**: Reminders scheduled based on medical specialty rules.
- ✅ **Convenient Data Upload**: Supports Excel spreadsheets, photo uploads (with vision OCR extraction), or direct WhatsApp uploads (sending register photos directly to the WhatsApp Business number).
- ✅ **Online Patient Booking**: Patients can schedule slots at any of the doctor's clinic locations using booking links.
- ✅ **Razorpay Payments**: Upfront booking fees collected to prevent fake bookings and reduce no-shows.
- ✅ **Daily PDF Schedules**: A structured PDF schedule (online bookings with walk-ins) delivered to the doctor's WhatsApp at midnight daily.
- ✅ **Guest Mode / Demo Sandbox**: Non-registered users can check the dashboard and play with mock stats, gating write actions with an auth modal.

---

## 3. Architecture Paradigm: Why Modular Monolith Over Microservices?

### Decision: Modular Monolith
The system is built as a **modular monolith**. It uses a single codebase (`services/fastapi/` for backend, `frontend/` for frontend) but can run as multiple containers (API server, Celery workers) in production.

```
                  ┌─────────────────┐
                  │  Vercel Static  │
                  │  React/Vite App │
                  └────────┬────────┘
                           │ HTTPS (REST API)
                           ▼
                 ┌───────────────────┐
                 │    Caddy Proxy    │
                 └─────────┬─────────┘
                           │ reverse-proxy
                           ▼
            ┌─────────────────────────────┐
            │       FastAPI Backend       │ (API Container)
            │  (Async API + APScheduler)  │
            └──────────────┬──────────────┘
                           │ Tasks Enqueue
                           ▼
                    ┌──────────────┐
                    │  Upstash TLS │ (Redis Queue & Cache)
                    │  Redis Broker│
                    └──────┬───────┘
                           │ Task Dequeue
                           ▼
            ┌─────────────────────────────┐
            │        Celery Worker        │ (Worker Container)
            │   (Same Code, Worker Entry) │
            └─────────────────────────────┘
```

### Key Rationale
1. **Simplicity & Velocity**: Easier local debugging, development, and unit testing within a single repository context.
2. **Reduced Latency & Network Overhead**: Shared relational database context prevents the need for complex, failure-prone distributed network requests.
3. **Transaction Reliability**: Full ACID database transaction guarantees across clinic locations, patients, appointments, and reminders without requiring Saga patterns.
4. **Team & Resource Efficiency**: Minimizes server overhead costs and eliminates the necessity of complex setups (Kubernetes, Service Meshes, API Gateways) for small development teams.
5. **Horizontal Scalability**: Despite a unified codebase, workload distribution is decoupled. The API server scales independently from the Celery background workers.

### Trade-offs Accepted
- **Tech Stack Lock-in**: All backend modules must share the same runtime (Python/FastAPI) and packages.
- **Deployment Cadence**: Deployments are all-or-nothing (a pipeline failure blocks both the API and worker deployments).

### When to Refactor to Microservices
- The engineering team expands beyond 10 developers, causing code ownership conflicts.
- Workloads like message generation (LLMs) or PDF rendering require specialized, highly-elastic scaling compared to general CRUD endpoints.
- Different components require different runtimes (e.g. Node.js or Go for high-performance I/O).

---

## 4. Component Details & Directory Mapping

The application codebase is strictly separated into distinct modules:

```
careremind/
├── docs/                      # Documentation (HLD, API Specs)
├── frontend/                  # React + TypeScript + Vite Frontend application
│   └── src/
│       ├── api/               # Axios services
│       ├── components/        # UI components (Layout, Guest gates, widgets)
│       ├── context/           # React contexts (Auth, GuestModeContext)
│       ├── pages/             # App Pages (Dashboard, Settings, Billing, Patients)
│       └── store/             # Zustand global state (Auth state)
└── services/
    └── fastapi/               # Unified Backend codebase
        └── app/
            ├── agents/        # LangGraph state machines & worker nodes
            ├── core/          # Configuration, Database engine, Integrations
            ├── features/      # Modular business features (CRUD routers, models, services)
            │   ├── auth/      # Doctor registry, login & Google OAuth
            │   ├── booking/   # Patient booking slots, serials & daily PDF
            │   ├── patients/  # Patient management & data encryption
            │   ├── reminders/ # Reminders scheduling & notification wrapper
            │   └── upload/    # Photo/Excel pipeline controller
            ├── middleware/    # Rate limiters, security headers, context
            ├── scheduler/     # In-process APScheduler registry
            ├── specialty/     # Medical specialty class registry
            └── worker/        # Celery application & background tasks
```

---

## 5. System Containers & Responsibilities

### 5.1 React Frontend
- **Technology**: React 19, Vite, TypeScript, Tailwind CSS, Zustand, Axios, React Router 6.
- **Responsibility**: Interactive dashboard for doctors. Allows them to upload registers, view patient lists, track scheduled reminders, manage clinic profiles, edit clinic locations, review daily appointment schedules, and subscribe to premium plans.
- **Key Design Patterns**:
  - **Guest Mode Sandbox**: Accessible without authorization via a `GuestModeProvider`. Normal users are guided with a banner and sandbox data. Write/edit actions are caught by a global hook `requireAuth()` that renders a login/signup modal.
  - **Mobile Responsiveness**: Pure CSS/Tailwind-based mobile design. Long tables use a custom `.overflow-x-auto` wrapper with minimum column widths. Complex navigation grids adapt to single-column flex configurations on mobile screens. Hover actions on desktop (like card edit/delete buttons) degrade gracefully to static visibility on touch screens.

### 5.2 FastAPI Backend
- **Technology**: FastAPI (async), SQLAlchemy 2.0 (async ORM), Pydantic v2 (data validation).
- **Responsibility**: Exposes a RESTful JSON API. Coordinates database persistence, token generation, webhook ingestion (WhatsApp/Razorpay), and initiates LangGraph workflows. Runs an in-process APScheduler instances for cron jobs.

### 5.3 PostgreSQL Database (Supabase)
- **Technology**: PostgreSQL 15, SQLAlchemy async pooling.
- **Responsibility**: Relational database storing isolated tenant settings, patient records, visits, billing invoices, bookings, and audit records.

### 5.4 Cache, Queue & Distributed Locks (Redis)
- **Technology**: Redis 7 (Upstash SSL/TLS enabled in production).
- **Responsibility**:
  - Task Broker for Celery tasks.
  - Results backend for task outcome logging.
  - Caching dashboard metrics (5-minute Time-To-Live).
  - Distributed locking (`scheduler_lock:{job_name}`) to prevent multiple FastAPI container replicas from executing the same scheduled job.

### 5.5 AI Agents (LangGraph & LangSmith)
- **Technology**: LangGraph (composable state graphs), OpenAI GPT-4o-mini (Vision OCR & text synthesis).
- **Responsibility**: Orchestrates multi-step cognitive flows (extraction, validation, deduplication, message compilation) with visibility provided via LangSmith tracing.

### 5.6 Background Workers (Celery)
- **Technology**: Celery 5.3 (multiprocess execution).
- **Responsibility**: Process asynchronous, long-running, or resource-heavy work out-of-band (e.g. sending bulk WhatsApp messages, OCR photo processing, midnight cleanup, retry loops).

---

## 6. AI Agent State Machines (LangGraph)

The system isolates operations into three specialized, stateful workflows:

```
1. Ingestion Graph (Patient Uploads)
   START ──► Route Ingestion ──► Extract Excel / OCR Photo ──► Deduplicate ──► Persist (DB) ──► END

2. Scheduling Graph (Reminder Setup)
   START ──► Resolve Medical Specialty ──► Map Timings ──► Create Reminders (DB) ──► END

3. Notification Graph (WhatsApp Send)
   START ──► Load Context ──► Check Opt-Out ──► Decrypt Phone ──► Format Message ──► Deliver WhatsApp ──► END
```

### 6.1 Ingestion Graph
- **Node: Route Ingestion**: Detects target file format (`excel`, `photo`) or checks if patient rows are pre-injected (Human-in-the-loop confirmation flow).
- **Node: Extract Excel**: Parses `.xlsx`/`.xls` upload logs using Pandas.
- **Node: Extract OCR**: Invokes GPT-4o-mini Vision with doctor register photos to synthesize structured patient JSON.
- **Node: Deduplicate**: Deterministically hashes incoming phone numbers (HMAC-SHA256) and matches them against existing patient records under the tenant context.
- **Node: Save to DB**: Inserts new patients and schedules next visits.

### 6.2 Scheduling Graph
- **Node: Resolve Medical Specialty**: Inspects the doctor's specialty (or specialty overrides in the appointment record) via the specialty registry lookup.
- **Node: Map Timings**: Fetches timing slots from the specialty instance (e.g., 7-day and 30-day follow-ups for all specialties).
- **Node: Create Reminders**: Inserts pending reminder records in the database, targeted for 9:00 AM IST on the computed date.

### 6.3 Notification Graph
- **Node: Load Context**: Loads related Tenant, Patient, and Appointment data from the database.
- **Node: Check Opt-Out**: Skips reminder creation if the patient record has `is_optout = True`.
- **Node: Decrypt Phone**: Decrypts the patient's phone number using AES-256 Fernet encryption.
- **Node: Format Message**: Synthesizes a patient message matching the doctor's language preference and specialty tone.
- **Node: Deliver WhatsApp**: Submits the message to the Meta Cloud API. If Meta fails, the reminder is marked as failed and flagged for retry (no SMS fallback is currently active in the core pipeline).

---

## 7. Medical Specialty Configuration System

Specialties govern reminder timing offset triggers, communication tones, and instructions.

| Specialty | Default Follow-up | Message Tone | Pre-Visit Instructions | Timings |
| :--- | :--- | :--- | :--- | :--- |
| **General Medicine / GP**| 30 days | Caring / Calm | General health check guidelines | 7 & 30 days |
| **Dental / Dentist** | 180 days | Gentle / Reassuring| Avoid eating for 1 hour before dental visits | 7 & 30 days |
| **Ophthalmology (Eye)** | 90 days | Precise / Gentle | Remove contact lenses before testing | 7 & 30 days |
| **Orthopedic** | 60 days | Supportive | Bring previous X-ray reports | 7 & 30 days |
| **Pediatric** | 30 days | Friendly / Warm | Bring child's vaccination card | 7 & 30 days |
| **Dermatology (Skin)** | 30 days | Precise / Calm | Do not apply makeup or creams before visit | 7 & 30 days |
| **Diagnostic Lab** | 30 days | Precise | Fast for 10-12 hours before test | 7 & 30 days |
| **Custom (Any other)** | User Defined | Friendly | General specialty follow-up guidelines | 7 & 30 days |

---

## 8. Detailed System Flows

### 8.1 User Registration & Login (Local Auth & Google OAuth)

```
                       DOCTOR / FRONTEND                     BACKEND / POSTGRES / GOOGLE
                       
  [Local Login]  ──►  POST /api/v1/auth/login  ───────────► Hashed password check (Argon2)
                                                             Generate JWT Token (HS256, 24h)
                                                 ◄────────── Return Token + Doctor metadata
                                                 
  [Google OAuth] ──►  Click "Login with Google"  ────────►   Redirect to Google OAuth consent screen
                                                             User grants permission
                      Google callback with OAuth token  ───► Verify token with Google APIs
                                                             Create / Find Tenant in DB
                                                             Generate JWT Token (HS256, 24h)
                                                 ◄────────── Redirect to Frontend dashboard url with Token
```

### 8.2 Ingestion & Upload Flow (Dashboard / WhatsApp Upload)

```
 DOCTOR                      FRONTEND / WEBHOOK              BACKEND / SUPABASE              LANGGRAPH
 
 [Dashboard] ───────►  POST /api/v1/upload/excel  ───────► Save raw files to Supabase Storage ─┐
                       or /api/v1/upload/photo                                                │
                                                                                              ▼
 [WhatsApp]  ───────►  Meta WhatsApp Media Webhook ──────► Ingest webhook media payload ─────► Ingestion Graph
                                                                                               ├─ Route File
                                                                                               ├─ Parse Excel/OCR
                                                                                               ├─ HMAC-SHA256 Dedup
                                                                                               └─ DB Persistence
                                                                                                      │
                                                                                                      ▼
                                                 ◄─────── Send results back to sender WhatsApp ◄──────┘
                                                          ("Processed 10 patients, 2 duplicates")
```

### 8.3 In-Process Scheduler & Celery Worker Execution

The scheduler (APScheduler) runs inside the FastAPI process, while background tasks are handled by Celery workers in separate containers.

```
       APScheduler (FastAPI Process)                       Upstash Redis                      Celery Workers
       
  [9:00 AM IST] ──► check distributed lock  ──► [Acquired] ──► Enqueue task  ──► [Broker Queue] ──► Fetch task
                                                                                                    │
                                                                                                    ▼
                                                                                            Execute Send Loop
                                                                                                    │
                                                                                                    ▼
                                                                                            Execute LangGraph
                                                                                             Notification Graph
                                                                                                    │
                                                                                                    ▼
                                                                                            Update DB Status
```

#### In-Process APScheduler Configuration
```python
# scheduler/jobs.py
SCHEDULED_JOBS = [
    {
        "func": generate_daily_schedules_job,
        "trigger": "cron",
        "hour": 0,
        "minute": 0,
        "id": "generate_daily_schedules",
        "name": "Generate Daily Schedules (Midnight)",
        "replace_existing": True,
    },
    {
        "func": cleanup_expired_reservations_job,
        "trigger": "interval",
        "minutes": 5,
        "id": "cleanup_expired_reservations",
        "name": "Cleanup Expired Reservations (Every 5 min)",
        "replace_existing": True,
    },
    {
        "func": dispatch_send_pending_reminders,
        "trigger": "cron",
        "hour": 9,
        "minute": 0,
        "id": "dispatch_send_pending_reminders",
        "name": "Dispatch Send Pending Reminders (9:00 AM IST)",
        "replace_existing": True,
    },
]
```

#### Redis Distributed Locking Helper
```python
# scheduler/jobs.py
async with distributed_lock("job_name", timeout=300) as acquired:
    if not acquired:
        return # Skip execution on secondary backend instances
    await execute_job()
```

### 8.4 Booking & Payment Flow (Razorpay Integration)

```
 PATIENT                     FRONTEND / WEBHOOK              BACKEND / DB / RAZORPAY
 
 Opens Booking Link  ─────►  GET Available Slots  ────────► Match selected doctor locations & times
 
 Selects Slot & Info ─────►  POST /booking/reserve ───────► Lock slot (expires in 10 minutes)
                                                             Generate Razorpay Order API Call
                                                 ◄────────── Return Razorpay order_id + details
 
 Patient Pays on Razorpay ──► Checkout widget popup
                               Razorpay webhook callback ───► Verify webhook signature (HMAC-SHA256)
                                                             Update booking status to CONFIRMED
                                                             Generate Receipt PDF (ReportLab)
                                                             Upload PDF to Supabase Storage
                                                 ◄────────── Return confirmation to patient & SMS link
```

---

## 9. External API Integration Specifications

### 9.1 Meta WhatsApp Business Cloud API

#### Base Endpoint
`POST https://graph.facebook.com/v21.0/{phone_number_id}/messages`

#### Headers
- `Authorization`: `Bearer {META_WHATSAPP_TOKEN}`
- `Content-Type`: `application/json`

#### Text Message Payload
```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "+919876543210",
  "type": "text",
  "text": {
    "body": "Hello Dr. Arjun Mehta's clinic wishes to remind you of your appointment tomorrow at 10:00 AM."
  }
}
```

#### Interactive Button Reply Message Payload
```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "+919876543210",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": {
      "text": "Hello from CareRemind. Confirm your appointment tomorrow."
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "confirm_appt_id_123",
            "title": "Confirm Booking"
          }
        }
      ]
    }
  }
}
```

### 9.2 Razorpay Payments API

#### Create Order Payload
- **Endpoint**: `POST https://api.razorpay.com/v1/orders`
- **Authentication**: Basic Authentication (`key_id:key_secret`)
```json
{
  "amount": 20000,
  "currency": "INR",
  "receipt": "receipt_booking_981",
  "partial_payment": false
}
```

#### Verify Payment Signature
```python
# booking/service.py
import hmac
import hashlib

expected_signature = hmac.new(
    key=RAZORPAY_SECRET.encode(),
    msg=f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
    digestmod=hashlib.sha256
).hexdigest()

if not hmac.compare_digest(expected_signature, razorpay_signature):
    raise SignatureVerificationError("Payment signature verification failed")
```

### 9.3 OpenAI Vision OCR API (GPT-4o-mini)

#### Payload
- **Endpoint**: `POST https://api.openai.com/v1/chat/completions`
```json
{
  "model": "gpt-4o-mini",
  "response_format": { "type": "json_object" },
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Identify the patient schedule or register records from this image. Extract columns: name, phone, next_visit_date (YYYY-MM-DD), specialty. Output as a JSON list under the key 'patients'."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,{base64_encoded_image_bytes}"
          }
        }
      ]
    }
  ]
}
```

---

## 10. Security & Compliance Design

### 10.1 Authentication & Multi-Tenancy
- **Authentication**: Stateless JWT token authentication with a 24-hour expiry using `HS256` signed secrets. Passwords hashed using GPU-resistant `Argon2`.
- **OAuth Integration**: Supports Google and Facebook logins, returning JWT tokens via URL query parameters on redirection back to the frontend.
- **Multi-Tenant Isolation**: Row-Level isolation enforced by `tenant_id` context routing. Custom SQL statements dynamically inject:
  ```python
  where(Model.tenant_id == current_tenant_id)
  ```
  This defends against Insecure Direct Object Reference (IDOR) exploits.

### 10.2 Cryptographic Data Protection
- **Phone Encryption**: Sensitive patient phone numbers are encrypted in database fields using symmetric cryptography (`Fernet AES-256`) via a shared secret key. Decrypted strictly at runtime before message dispatch.
- **Deterministic Phone Hashing**: To allow tenant-level deduplication without storing raw phone numbers or running brute-force decryption loops, phone numbers are hashed using a deterministic secret key (`HMAC-SHA256`).

### 10.3 Network & API Hardening
- **HTTPS Enforced**: Reversed proxied by a Caddy configuration to provide automatic Let's Encrypt SSL certificates.
- **CORS Whitelists**: Direct client-facing endpoints explicitly configure origin headers, restricting access to designated domains.
- **Security Headers**: Standard headers injected into response streams via `SecurityHeadersMiddleware`:
  - `X-Content-Type-Options: nosniff` (mime protection)
  - `X-Frame-Options: DENY` (anti-clickjacking)
  - `X-XSS-Protection: 1; mode=block` (browser filter)
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains` (HSTS)
- **IP & User Rate Limiting**: Managed by a Redis key increment counter, falling back to open execution if Redis connection fails:
  - Auth endpoints: 10 requests / minute / IP
  - Anonymous global: 200 requests / minute / IP
  - Authenticated user: 1000 requests / minute / user context

---

## 11. Performance Optimizations & Connection Pooling

### 11.1 HTTP Client connection pooling
The API container establishes a shared `httpx.AsyncClient` lifecycle handler on startup to prevent resource exhaustion from duplicate port bindings.

```python
# main.py lifespan
app.state.http_client = httpx.AsyncClient(
    timeout=30.0,
    limits=httpx.Limits(
        max_connections=100,          # Maximum simultaneous sockets
        max_keepalive_connections=20  # Reusable pooled connections
    )
)
```

### 11.2 Database Session connection pooling
SQLAlchemy configuration pools database connections to match FastAPI concurrency targets.

```python
# core/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=15,          # Active persistent connections per Gunicorn worker thread
    max_overflow=5,        # Maximum overflow connections during spike periods
    pool_pre_ping=True,    # Verify connection availability prior to issuing statements
    pool_recycle=3600,     # Cycle connection lifetime every 1 hour to prevent stale sockets
)
```

---

## 12. Deployment Architecture

### 12.1 Local Sandbox Environment
Running the system locally requires Docker and docker-compose. Local databases and Redis services run alongside the web and worker processes.

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  api:
    build: ./services/fastapi
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
  worker:
    build: ./services/fastapi
    command: celery -A app.worker.celery_app worker --loglevel=info
```

### 12.2 Production Environment
In production, the architecture decouples static web assets, APIs, backends, databases, caching layers, and background tasks.

```
                  ┌────────────────────┐
                  │    React Client    │
                  │   Vercel Hosting   │
                  └─────────┬──────────┘
                            │ HTTPS (REST API)
                            ▼
              ┌────────────────────────────┐
              │    Automatic SSL Proxy     │
              │       Caddy Server         │
              └─────────────┬──────────────┘
                            │ Reverse Proxy
                            ▼
     ┌──────────────────────────────────────────────┐
     │           FastAPI API Containers             │
     │      (Gunicorn runner - 4 Workers)           │
     └──────────────┬────────────────┬──────────────┘
                    │                │
      SQL (Async)   │                │ Enqueue Task
                    ▼                ▼
     ┌──────────────────────┐┌──────────────────────┐
     │ Supabase PostgreSQL  ││   Upstash Redis DB   │
     │   (Cloud Managed)    ││   (Cloud / TLS)      │
     └──────────────────────┘└──────────┬───────────┘
                                        │
                                        │ Dequeue Task
                                        ▼
                            ┌──────────────────────┐
                            │    Celery Workers    │
                            │  (3 Replicas Active) │
                            └──────────────────────┘
```

- **Static Frontend**: Compiled into optimized production bundles by Vite and served via Vercel for fast page loads.
- **Caddy Web Server**: Handles ingress path routing and automatically manages TLS certificates via Let's Encrypt.
- **FastAPI API Server**: Managed by Gunicorn using 4 Async Uvicorn worker threads to maximize CPU utilization. Runs APScheduler inside the process memory.
- **Celery Worker Replicas**: Decoupled cluster running 3 active replicas processing tasks asynchronously from the Upstash Redis broker queue.

---

## 13. Scope Matrix

### In Scope
- Multi-tenant doctor directory registration and authentication.
- Bulk patient lists upload with spreadsheet analysis and image OCR parsing.
- Automated WhatsApp notifications scheduling with specialty-specific rules.
- Patient booking links, calendar slot reservations, and payments.
- Automatic generation and delivery of daily schedules (PDF) to the doctor's WhatsApp.
- Rate limiting, IDOR prevention, and cryptographic patient record protection (encryption and hashing).
- Core UI pages with mobile responsiveness.

### Out of Scope
- Voice call reminders or interactive voice response (IVR).
- Custom patient mobile applications (WhatsApp is the primary interface).
- Electronic Health Record (EHR) systems, prescription management, and clinical charting.
- Storing debit/credit card credentials (delegated entirely to Razorpay).
- Multi-practitioner clinic environments (supported users are individual doctors).
- Local offline mode (requires active internet access).
