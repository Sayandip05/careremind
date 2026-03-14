# CareRemind V1 — What's Still Remaining

> These are the missing pieces to make V1 **production-ready** and **interview-impressive**.  
> Priority: 🔴 Must-have → 🟡 Should-have → 🟢 Nice-to-have

---

## 🔴 Must-Have (Complete the Backend)

### 1. Testing & Code Quality (#19)
**Status:** ❌ Not started  
**Why it matters:** Every interviewer will ask "do you have tests?"

**What to build:**
- `pytest` + `pytest-asyncio` for FastAPI async testing
- `httpx.AsyncClient` for API endpoint tests
- Test files:
  - `tests/test_auth.py` — register, login, token validation, duplicate email
  - `tests/test_patients.py` — CRUD, pagination, IDOR protection
  - `tests/test_upload.py` — Excel parsing, photo OCR mock
  - `tests/test_reminders.py` — listing, status filtering
- **Mocking:** Mock external APIs (WhatsApp, GPT-4o) with `unittest.mock`
- **Fixtures:** Shared test database session, test tenant, test patient
- `conftest.py` with test database setup

**Estimated effort:** 3-4 hours

---

### 2. Redis API Caching (#9)
**Status:** ⚠️ Redis exists as Celery broker, no API caching  
**Why it matters:** Shows you understand caching patterns (interview topic)

**What to build:**
- Cache `/dashboard/stats` response for 5 minutes (most-hit endpoint)
- Cache `/patients?page=1` for 2 minutes (frequently loaded)
- Invalidate cache on new upload or patient creation
- Use `redis-py` async client with `json.dumps`/`json.loads`

**Estimated effort:** 1-2 hours

---

### 3. Object Storage (#20)
**Status:** ⚠️ `storage.py` exists but is a placeholder  
**Why it matters:** Uploaded files need to persist somewhere

**What to build:**
- Connect `storage.py` to **Supabase Storage** (free tier, already have account)
- Upload Excel/Photo files to a `uploads/{tenant_id}/` bucket
- Return public URL to store in `UploadLog.storage_url`
- Delete files on cleanup

**Estimated effort:** 1-2 hours

---

### 4. Admin Panel (Owner Dashboard)
**Status:** ⚠️ Frontend done, backend API needed  
**Why it matters:** You (as the platform owner) need to see who's using your platform

**Frontend:** ✅ `/admin` page in dashboard (platform stats + doctors table)

**Backend still needed:**
- Add `is_superadmin` field to `Tenant` model
- New routes at `/api/v1/admin/`:
  - `GET /admin/tenants` — list all signed-up doctors
  - `GET /admin/stats` — platform-wide stats (total doctors, total patients, total reminders)
  - `PATCH /admin/tenants/{id}` — activate/deactivate a doctor
- Protect with `get_current_superadmin` dependency

**Estimated effort:** 1-2 hours (backend only)

---

## 🟡 Should-Have (Polish for Interviews)

### 5. Email Sending (#24)
**Status:** ❌ Not started  
**Why it matters:** Professional apps send confirmation emails

**What to build:**
- Welcome email on doctor registration
- Daily summary email (alongside WhatsApp)
- Use **Resend** or **SendGrid** free tier (100 emails/day)
- Email templates in `app/services/email_service.py`

**Estimated effort:** 1-2 hours

---

### 6. Observability (#13)
**Status:** ⚠️ Basic logging exists, no metrics  
**Why it matters:** Shows production-readiness mindset

**What to build:**
- `prometheus-fastapi-instrumentator` for automatic metrics
- Custom metrics: requests/sec, upload processing time, reminder send rate
- Health endpoint already exists — add DB connectivity check
- Structured logging with request IDs

**Estimated effort:** 1-2 hours

---

### 7. Alembic Migrations
**Status:** ⚠️ Alembic in requirements but no migration files  
**Why it matters:** Shows proper database change management

**What to build:**
- `alembic init` in fastapi directory
- Initial migration from current models
- Migration for any new fields (e.g., `is_superadmin`)

**Estimated effort:** 30 minutes

---

## 🟢 Nice-to-Have (Bonus Points)

### 8. WebSockets (#21)
**What:** Real-time upload progress bar on the dashboard  
**Effort:** 2-3 hours

### 9. Rate Limiting
**What:** Prevent API abuse (especially on login endpoint)  
**Effort:** 30 minutes with `slowapi`

### 10. API Key Authentication
**What:** Alternative auth for programmatic access  
**Effort:** 1 hour

---

## 🔵 Production Deployment (Azure / AWS)

### Containerized Deployment
**Target:** Azure Container Apps or AWS ECS (Fargate)

**What's needed:**
- `Dockerfile` per service (FastAPI, Worker, Scheduler, Dashboard, Landing)
- `docker-compose.prod.yml` with production overrides
- Container registry: **Azure ACR** or **AWS ECR**
- Managed PostgreSQL: **Azure Database for PostgreSQL** or **AWS RDS**
- Managed Redis: **Azure Cache for Redis** or **AWS ElastiCache**
- Object Storage: **Azure Blob Storage** or **AWS S3**
- CI/CD: **GitHub Actions** → build → push → deploy
- Environment variables via secrets manager (Azure Key Vault / AWS Secrets Manager)
- Custom domain + SSL via **Azure Front Door** or **AWS CloudFront + ACM**
- Monitoring: **Azure Monitor** or **AWS CloudWatch** + Prometheus/Grafana

### Deployment architecture:
```
Internet → CDN (CloudFront/Front Door)
  ├── /          → Landing Page (static, served from CDN)
  ├── /dashboard → Dashboard SPA (static, served from CDN)
  └── /api/*     → FastAPI Container (auto-scaling)
                    ├── Worker Container (Celery)
                    ├── Scheduler Container (APScheduler)
                    ├── Redis (managed)
                    └── PostgreSQL (managed)
```

---

## Recommended Build Order

```
Day 1: Tests (most impactful for interviews)
Day 2: Admin Panel backend + Redis Caching
Day 3: Object Storage + Email
Day 4: Alembic Migrations + Observability
Day 5: Docker production config + CI/CD
```

