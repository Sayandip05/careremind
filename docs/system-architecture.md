# System Architecture - CareRemind

**Version**: 1.0  
**Last Updated**: 2026-04-30  
**Status**: Production-Ready

---

## Overview

CareRemind is a **modular monolith** built with FastAPI, designed for **individual doctors in India** to automate appointment reminders via WhatsApp and SMS.

**Primary User**: Individual doctors (who may have multiple clinic locations)  
**Architecture Style**: Modular Monolith (Single codebase, multiple containers)

---

## Why Modular Monolith Over Microservices?

### Decision: Modular Monolith

**Reasons**:
1. **Simplicity**: Single codebase, easier to develop and debug
2. **Performance**: No network overhead between services
3. **Transactions**: ACID guarantees across all operations
4. **Team Size**: Small team (1-3 developers) - microservices add unnecessary complexity
5. **Deployment**: Single deployment unit, easier CI/CD
6. **Cost**: Lower infrastructure costs (fewer servers, no service mesh)

**Trade-offs Accepted**:
- Cannot scale individual components independently (but we don't need to)
- All components share same tech stack (Python/FastAPI)
- Deployment is all-or-nothing (acceptable for our release cadence)

**When to Consider Microservices**:
- Team grows beyond 10 developers
- Need to scale specific components independently (e.g., reminder sending)
- Different components need different tech stacks

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CAREREMIND SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────────────────────┐ │
│  │   React      │◄────────┤   FastAPI Backend            │ │
│  │   Frontend   │  HTTPS  │   (Async + APScheduler)      │ │
│  │   (Vite)     │         │                              │ │
│  └──────────────┘         └──────────┬───────────────────┘ │
│                                       │                      │
│                    ┌──────────────────┼──────────────┐      │
│                    │                  │              │      │
│            ┌───────▼────┐  ┌──────────▼──────┐  ┌───▼────┐│
│            │ PostgreSQL │  │    Redis        │  │Supabase││
│            │ (Supabase) │  │ (Cache/Queue/   │  │(Storage││
│            │            │  │  Locks)         │  │        ││
│            └────────────┘  └─────────────────┘  └────────┘│
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         CELERY WORKERS (Separate Container)          │  │
│  │  (Same codebase, different entry point)              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         EXTERNAL SERVICES                             │  │
│  │  WhatsApp │ SMS │ Razorpay │ OpenAI │ NVIDIA         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. FastAPI Backend
- **Location**: `services/fastapi/`
- **Runs**: API server + APScheduler (in-process)
- **Port**: 8000 (dev), internal (prod)
- **Responsibilities**:
  - REST API endpoints
  - JWT authentication
  - Business logic
  - Scheduled jobs (APScheduler)
  - AI agent orchestration

### 2. Celery Workers
- **Location**: `services/fastapi/` (same codebase)
- **Entry Point**: `celery -A app.worker.celery_app worker`
- **Responsibilities**:
  - Send reminders (WhatsApp/SMS)
  - Retry failed reminders
  - Generate daily summaries
  - Cleanup old data

### 3. PostgreSQL Database
- **Provider**: Supabase (managed)
- **Purpose**: Primary data store
- **Tables**: 10 tables (tenants, patients, appointments, reminders, bookings, etc.)

### 4. Redis
- **Purpose**: Cache + Queue + Locks
- **Uses**:
  - Celery broker
  - Distributed locking
  - Dashboard stats caching (5 min TTL)

### 5. React Frontend
- **Location**: `frontend/`
- **Build**: Vite
- **Deployment**: Vercel (static hosting)

---

## Request/Response Flows

### Flow 1: User Registration & Login

```
User → Frontend → POST /api/v1/auth/register
                    ↓
                  FastAPI validates input (Pydantic)
                    ↓
                  Hash password (Argon2)
                    ↓
                  Save to PostgreSQL (tenants table)
                    ↓
                  Generate JWT token (HS256, 24h expiry)
                    ↓
                  Return token + tenant info
                    ↓
Frontend stores token in localStorage
```

**OAuth Flow (Google/Facebook)**:
```
User clicks "Login with Google"
  ↓
Frontend → GET /api/v1/auth/login/google
  ↓
FastAPI redirects to Google OAuth
  ↓
User authorizes on Google
  ↓
Google redirects to /api/v1/auth/callback/google
  ↓
FastAPI verifies OAuth token
  ↓
Create/update tenant in database
  ↓
Generate JWT token
  ↓
Redirect to frontend with token in URL
  ↓
Frontend extracts token and stores it
```

---

### Flow 2: Patient Data Upload (3 Options)

**Option 1: Dashboard Upload (Excel)**
```
Doctor uploads Excel file via web dashboard
  ↓
Frontend → POST /api/v1/upload/excel (multipart/form-data)
  ↓
FastAPI validates file (max 10MB, .xlsx/.xls only)
  ↓
Save file to Supabase Storage
  ↓
Create UploadLog record (status=PROCESSING)
  ↓
Trigger Ingestion Graph (LangGraph):
  ├─ Route Node: Detect file type (excel)
  ├─ Extract Node: Parse Excel → list of patient rows
  ├─ Dedup Node: Check phone_hash against DB
  └─ Save Node: Insert new patients + appointments
  ↓
Trigger Scheduling Graph (LangGraph):
  ├─ Resolve specialty timing rules
  └─ Create Reminder records (status=PENDING, scheduled_at=9 AM)
  ↓
Update UploadLog (status=COMPLETED, stats)
  ↓
Return result to frontend
```

**Option 2: WhatsApp Upload (Photo/Excel)**
```
Doctor sends patient register photo/Excel to WhatsApp Business number
  ↓
POST /api/v1/webhooks/whatsapp (from Meta)
  ↓
FastAPI downloads media from Meta API
  ↓
Identify doctor by WhatsApp number (Tenant.whatsapp_number)
  ↓
Create UploadLog record (status=PROCESSING)
  ↓
Trigger Ingestion Graph (LangGraph):
  ├─ Route Node: Detect file type (photo/excel)
  ├─ Extract Node: OCR (GPT-4o Mini) or Parse Excel
  ├─ Dedup Node: Check phone_hash against DB
  └─ Save Node: Insert new patients + appointments
  ↓
Trigger Scheduling Graph (LangGraph):
  ├─ Resolve specialty timing rules
  └─ Create Reminder records (status=PENDING, scheduled_at=9 AM)
  ↓
Update UploadLog (status=COMPLETED, stats)
  ↓
Send WhatsApp reply with results (X patients added, Y duplicates)
```

**Option 3: Dashboard Upload (Photo)**
```
Doctor uploads photo via web dashboard
  ↓
Frontend → POST /api/v1/upload/photo (multipart/form-data)
  ↓
FastAPI validates file (max 20MB, image/* only)
  ↓
Save file to Supabase Storage
  ↓
Create UploadLog record (status=PROCESSING)
  ↓
Trigger Ingestion Graph (LangGraph):
  ├─ Route Node: Detect file type (photo)
  ├─ Extract Node: OCR with GPT-4o Mini vision
  ├─ Dedup Node: Check phone_hash against DB
  └─ Save Node: Insert new patients + appointments
  ↓
Trigger Scheduling Graph (LangGraph):
  ├─ Resolve specialty timing rules
  └─ Create Reminder records (status=PENDING, scheduled_at=9 AM)
  ↓
Update UploadLog (status=COMPLETED, stats)
  ↓
Return result to frontend
```

---

### Flow 3: Reminder Sending (Background Job)

```
9:00 AM IST - APScheduler triggers job
  ↓
Scheduler dispatches Celery task: send_pending_reminders
  ↓
Celery worker picks up task
  ↓
Fetch all reminders where:
  - status = PENDING
  - scheduled_at <= now
  - tenant is active
  ↓
For each reminder:
  ├─ Run Notification Graph (LangGraph):
  │   ├─ Load context (patient, appointment, tenant)
  │   ├─ Check if patient opted out → skip
  │   ├─ Decrypt phone number
  │   ├─ Generate personalized message (AI)
  │   ├─ Try WhatsApp send (with retry)
  │   └─ Fallback to SMS if WhatsApp fails
  │
  └─ Update reminder status (SENT/FAILED)
  ↓
Log summary (X sent, Y failed)
```

---

### Flow 4: Patient Booking (Web Dashboard/Link)

```
Patient receives reminder with booking link (via WhatsApp/SMS)
  ↓
Patient opens link in browser → Booking page
  ↓
GET /api/v1/booking/clinics
  ↓
FastAPI returns doctor's clinic locations
  ↓
Patient selects clinic and date
  ↓
GET /api/v1/booking/slots?clinic_id=X&date=Y
  ↓
FastAPI returns available slots (9 AM - 5 PM, 30-min intervals)
  ↓
Patient selects slot
  ↓
POST /api/v1/booking/reserve
  ├─ Create booking (status=RESERVED, expires in 10 min)
  ├─ Create Razorpay order
  └─ Return order_id + payment details
  ↓
Patient completes payment on Razorpay
  ↓
POST /api/v1/booking/confirm
  ├─ Verify payment signature (HMAC-SHA256)
  ├─ Update booking (status=CONFIRMED)
  ├─ Generate PDF bill
  └─ Return confirmation
  ↓
Midnight: Assign serial numbers to confirmed bookings
  ↓
Midnight: Generate daily schedule PDF (per clinic location)
  ↓
Send PDF to doctor's WhatsApp
```

**Note**: Booking is done via web interface (dashboard or link), not via WhatsApp button. Doctor can have multiple clinic locations (e.g., "Morning Clinic", "Evening Clinic").

---

## Authentication Flow

### JWT Token Flow

```
1. User logs in → FastAPI generates JWT
   - Payload: {sub: tenant_id, email: email, exp: 24h}
   - Algorithm: HS256
   - Secret: JWT_SECRET_KEY (from env)

2. Frontend stores token in localStorage

3. Every API request:
   - Frontend sends: Authorization: Bearer <token>
   - AuthMiddleware logs request
   - Route dependency (get_current_tenant):
     ├─ Extract token from header
     ├─ Verify signature + expiry
     ├─ Load tenant from database
     └─ Return tenant object

4. Token expires after 24 hours → user must re-login
```

### Multi-Tenant Isolation

```
Every database query is filtered by tenant_id:

# Example
result = await db.execute(
    select(Patient).where(
        Patient.tenant_id == current_tenant.id,
        Patient.id == patient_id
    )
)

This prevents IDOR attacks (Insecure Direct Object Reference)
```

---

## Background Job Flow (Celery + APScheduler)

### APScheduler (In-Process with FastAPI)

**Jobs**:
```python
# Midnight (00:00 IST)
- generate_daily_schedules_job()  # Direct execution
- dispatch_midnight_cleanup()     # Dispatch to Celery

# Every 5 minutes
- cleanup_expired_reservations_job()  # Direct execution

# 9:00 AM IST
- dispatch_send_pending_reminders()  # Dispatch to Celery

# 9:30 AM IST
- dispatch_generate_daily_summary()  # Dispatch to Celery

# 11:00 AM IST
- dispatch_retry_failed_reminders()  # Dispatch to Celery
```

**Distributed Locking**:
```python
async with distributed_lock("job_name", timeout=300):
    # Only one instance runs this job
    # Lock auto-expires after 5 minutes
    await execute_job()
```

### Celery Workers

**Tasks**:
```python
# app/worker/tasks/reminder_tasks.py
@celery_app.task
def send_pending_reminders():
    # Fetch pending reminders
    # Send via WhatsApp/SMS
    # Update status

@celery_app.task
def retry_failed_reminders():
    # Fetch failed reminders (retry_count < 2)
    # Retry sending
    # Update status

# app/worker/tasks/report_tasks.py
@celery_app.task
def generate_daily_summary():
    # Aggregate stats
    # Send to doctor via WhatsApp

# app/worker/tasks/cleanup_tasks.py
@celery_app.task
def cleanup_old_uploads():
    # Delete files older than 30 days

@celery_app.task
def cleanup_expired_reminders():
    # Archive reminders older than 90 days
```

---

## External Integrations

### 1. WhatsApp (Meta Cloud API)

**Purpose**: Primary reminder channel + Doctor upload channel

**Flow (Sending Reminders)**:
```
FastAPI → POST https://graph.facebook.com/v21.0/{phone_id}/messages
Headers:
  - Authorization: Bearer {META_WHATSAPP_TOKEN}
Body:
  {
    "messaging_product": "whatsapp",
    "to": "+919876543210",
    "type": "text",
    "text": {"body": "Your appointment is tomorrow..."}
  }

Response:
  {
    "messages": [{"id": "wamid.xxx"}]
  }
```

**Retry Logic**: 3 attempts with exponential backoff (2s, 4s, 8s)

**Webhook (Incoming Messages from Doctor)**:
```
WhatsApp → POST /api/v1/webhooks/whatsapp
  - Opt-out keywords (STOP, unsubscribe) → mark patient as opted out
  - Image uploads → trigger OCR pipeline (doctor sends patient register photos)
  - Document uploads → trigger Excel pipeline (doctor sends Excel files)
  - Unknown text → send help message

Doctor sends photo/Excel → System processes → Replies with results
```

**Daily Schedule Delivery**:
```
Midnight job generates PDF schedule → Sends to doctor's WhatsApp
Doctor receives PDF with all confirmed bookings for the day
```

---

### 2. SMS (Fast2SMS)

**Purpose**: Fallback when WhatsApp fails

**Flow**:
```
FastAPI → POST https://www.fast2sms.com/dev/bulkV2
Headers:
  - authorization: {FAST2SMS_API_KEY}
Body:
  {
    "route": "v3",
    "sender_id": "CAREMD",
    "message": "Your appointment is tomorrow...",
    "language": "english",
    "numbers": "9876543210"
  }

Response:
  {
    "return": true,
    "message": ["SMS sent successfully"]
  }
```

**Retry Logic**: 3 attempts with exponential backoff

**Truncation**: SMS limited to 160 characters (warning logged if truncated)

---

### 3. Razorpay (Payments)

**Purpose**: Online booking payments

**Flow**:
```
1. Create Order:
   FastAPI → POST https://api.razorpay.com/v1/orders
   Auth: Basic {key_id}:{key_secret}
   Body: {"amount": 20000, "currency": "INR"}
   Response: {"id": "order_xxx", "amount": 20000}

2. Patient Pays:
   Frontend → Razorpay Checkout
   User enters card details
   Razorpay processes payment

3. Verify Payment:
   Frontend → POST /api/v1/booking/confirm
   Body: {
     "razorpay_order_id": "order_xxx",
     "razorpay_payment_id": "pay_xxx",
     "razorpay_signature": "abc123..."
   }
   
   FastAPI verifies signature:
   expected = HMAC-SHA256(order_id|payment_id, secret)
   if expected == signature:
     booking.status = CONFIRMED
```

**Webhook** (Server-to-Server):
```
Razorpay → POST /api/v1/webhooks/razorpay
Headers:
  - X-Razorpay-Signature: {signature}
Body:
  {
    "event": "payment.captured",
    "payload": {...}
  }

FastAPI verifies webhook signature (HMAC-SHA256)
```

**Idempotency**: Uses `X-Prazorpay-Idempotency-Key` header to prevent duplicate orders

---

### 4. OpenAI / NVIDIA (Vision/OCR)

**Purpose**: Extract patient data from photos

**Flow**:
```
FastAPI → POST https://api.openai.com/v1/chat/completions
Headers:
  - Authorization: Bearer {OPENAI_API_KEY}
Body:
  {
    "model": "gpt-4o-mini",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "Extract patient data..."},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }]
  }

Response:
  {
    "choices": [{
      "message": {
        "content": "{\n  \"patients\": [{\"name\": \"...\", \"phone\": \"...\"}]\n}"
      }
    }]
  }
```

**Retry Logic**: 3 attempts with exponential backoff

**Fallback**: NVIDIA API if OpenAI fails

---

### 5. Supabase (Storage)

**Purpose**: File uploads (Excel, photos, PDFs)

**Flow**:
```
FastAPI → POST https://{project}.supabase.co/storage/v1/object/{bucket}/{path}
Headers:
  - Authorization: Bearer {SUPABASE_SERVICE_KEY}
Body: (binary file data)

Response:
  {
    "Key": "uploads/tenant_id/file.xlsx"
  }

Public URL:
  https://{project}.supabase.co/storage/v1/object/public/{bucket}/{path}
```

---

## Security Decisions

### 1. Password Hashing: Argon2
- **Why**: OWASP recommended, resistant to GPU attacks
- **Library**: `pwdlib` (Python)
- **Config**: Default recommended settings

### 2. Phone Encryption: Fernet (AES-256)
- **Why**: Symmetric encryption, fast, secure
- **Key**: `FIELD_ENCRYPTION_KEY` (env variable)
- **Usage**: Encrypt before storage, decrypt before sending

### 3. Phone Deduplication: HMAC-SHA256
- **Why**: Deterministic hash for duplicate detection
- **Key**: Same as encryption key
- **Usage**: Hash phone → check if exists → skip if duplicate

### 4. JWT Tokens: HS256
- **Why**: Simple, fast, sufficient for single-server setup
- **Expiry**: 24 hours
- **Secret**: `JWT_SECRET_KEY` (env variable)

### 5. Payment Verification: HMAC-SHA256
- **Why**: Razorpay standard, prevents payment spoofing
- **Secret**: `RAZORPAY_SECRET` (env variable)

### 6. HTTPS: Caddy (Auto-HTTPS)
- **Why**: Automatic Let's Encrypt certificates
- **Config**: `Caddyfile` (reverse proxy)

### 7. CORS: Whitelist Only
- **Why**: Prevent unauthorized frontend access
- **Config**: `CORS_ORIGINS` (env variable)

### 8. Rate Limiting: IP-based
- **Why**: Prevent abuse
- **Config**: Middleware (100 requests/minute per IP)

---

## Connection Pooling

### HTTP Connections
```python
# Shared HTTP client (main.py lifespan)
app.state.http_client = httpx.AsyncClient(
    timeout=30.0,
    limits=httpx.Limits(
        max_connections=100,      # Total connections
        max_keepalive_connections=20  # Reusable connections
    )
)

# Injected into all services
whatsapp_service.set_http_client(app.state.http_client)
sms_service.set_http_client(app.state.http_client)
razorpay_service.set_http_client(app.state.http_client)
```

### Database Connections
```python
# SQLAlchemy async engine
engine = create_async_engine(
    DATABASE_URL,
    pool_size=15,           # Connections per worker
    max_overflow=5,         # Extra connections if needed
    pool_pre_ping=True,     # Verify connection before use
    pool_recycle=3600,      # Recycle after 1 hour
)

# 4 Gunicorn workers × 15 connections = 60 total
```

---

## Deployment Architecture

### Development
```
docker-compose up
  ├─ api (FastAPI + APScheduler) - port 8000
  ├─ worker (Celery) - same image, different command
  ├─ postgres - port 5432
  ├─ redis - port 6379
  └─ frontend (Vite dev server) - port 3000
```

### Production
```
docker-compose -f docker-compose.prod.yml -f docker-compose.caddy.yml up
  ├─ caddy (reverse proxy) - ports 80, 443
  ├─ api (Gunicorn + APScheduler) - 4 workers
  ├─ worker (Celery) - 3 replicas
  └─ redis (AOF persistence)

External:
  ├─ PostgreSQL (Supabase)
  ├─ Storage (Supabase)
  └─ Frontend (Vercel)
```

---

## Summary

CareRemind uses a **modular monolith architecture** for simplicity and performance:

- **Doctor-centric workflow**: Individual doctors are the primary users, managing their own patients across multiple clinic locations
- **3 upload options**: Dashboard (Excel/Photo) or WhatsApp (Photo/Excel) - doctor chooses what's convenient
- **WhatsApp as primary channel**: Reminders sent to patients, schedules sent to doctors, uploads received from doctors
- **Single codebase** (`services/fastapi/`) with clear module boundaries
- **Two containers**: API server + Celery workers (same code, different entry points)
- **Async throughout**: FastAPI, SQLAlchemy, httpx for high concurrency
- **Distributed locking**: Redis prevents duplicate job execution
- **Connection pooling**: HTTP and database connections reused
- **Security-first**: Argon2, AES-256, HMAC-SHA256, JWT, HTTPS
- **Graceful degradation**: Works even if external services fail

**When to refactor to microservices**: Team > 10 developers, need independent scaling, or different tech stacks required.

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-30  
**Status**: Production-Ready
