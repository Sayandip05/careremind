# CareRemind V1 — Complete Production Audit & Fix Plan

Full line-by-line audit of every file in the V1 workflow against the user's flow specification. Every bug found, every fix scoped, prioritized by severity.

---

## User Review Required

> [!CAUTION]
> ### 2 Critical Data-Integrity Bugs Found
> **Bug 1 — Dedup is completely broken.** `dedup_agent.py` encrypts each phone with Fernet and compares against stored encrypted phones. But Fernet is **non-deterministic** — encrypting the same phone number twice produces different ciphertext each time. So the `IN` query on line 50-55 will **NEVER** find matches. Every upload will create duplicate patients. Same bug exists in `patients/service.py` line 31-37.
> 
> **Bug 2 — Reminders are never scheduled.** The ingestion pipeline (`extract → dedup → save_to_db → END`) saves Patients + Appointments but **never calls** `ReminderAgent.schedule_reminders()`. The scheduling graph exists but is completely disconnected from the ingestion graph. No upload (via dashboard or WhatsApp) will ever create reminder records.

> [!IMPORTANT]
> ### Decisions Needed
> 1. **Dedup fix strategy**: I'll add a `phone_hash` column (deterministic HMAC-SHA256) to the `patients` table for dedup lookups, keeping the existing `phone_encrypted` (Fernet) for secure decryption. This requires an Alembic migration. Approve?
> 2. **Docker**: The dev `docker-compose.yml` references a broken nginx (only a README.md exists in `infrastructure/nginx/`). Should I replace it with Caddy everywhere, or remove the reverse proxy from dev compose entirely?
> 3. **OAuth redirect URIs**: Currently hardcoded to `localhost:8000`. I'll make them dynamic via `settings.API_BASE_URL`. Approve?

---

## All Issues Found (Prioritized)

### 🔴 P0 — Data Integrity / Workflow Broken

| # | File | Bug |
|---|---|---|
| 1 | [dedup_agent.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/agents/dedup_agent.py#L44) | **Fernet is non-deterministic** — `encrypt(phone)` produces different ciphertext each call. The `WHERE phone_encrypted IN (...)` query on L50-55 will NEVER match existing patients. Dedup is completely broken. |
| 2 | [patients/service.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/patients/service.py#L28-L37) | Same Fernet dedup bug — `create_patient()` encrypts phone and checks `WHERE phone_encrypted == encrypted`. Will never find existing patients. |
| 3 | [persistence.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/agents/nodes/persistence.py) | **Reminders never scheduled** — `save_to_db_node` creates Patient + Appointment records but never calls `ReminderAgent.schedule_reminders()`. The scheduling graph is completely disconnected from the ingestion graph. |
| 4 | [security.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/core/security.py#L76-L82) | `EncryptionService` auto-generates ephemeral Fernet key when `FIELD_ENCRYPTION_KEY` is empty. On server restart, all previously encrypted phones become **permanently undecryptable**. |

### 🔴 P1 — Runtime Errors / Crashes

| # | File | Bug |
|---|---|---|
| 5 | [auth/router.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/auth/router.py#L32-L43) | OAuth `redirect_uri` hardcoded to `http://localhost:8000`. Will return 500 in any non-local environment. |
| 6 | [auth/router.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/auth/router.py#L56) | OAuth callback: if provider returns `openid=None` or `openid.email=None` (Facebook without email perm), code crashes with `AttributeError`. |
| 7 | [upload/router.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/upload/router.py#L70) | `UploadStatus.COMPLETED.value` (string) assigned to an Enum column — inconsistent with line 136 which uses `UploadStatus.COMPLETED`. Should be enum everywhere. |
| 8 | [docker-compose.yml](file:///c:/Users/sayan/DEVELOPEMENT/careremind/docker-compose.yml#L4-L14) | `nginx` service builds from `./infrastructure/nginx` which has no Dockerfile — only a README.md. `docker-compose up` will crash. |
| 9 | [docker-compose.yml](file:///c:/Users/sayan/DEVELOPEMENT/careremind/docker-compose.yml#L82) | `prometheus:latest` — invalid image name. Correct is `prom/prometheus:latest`. |

### 🟡 P2 — Missing V1 Workflow Steps

| # | File | Gap |
|---|---|---|
| 10 | auth/service.py | **No welcome WhatsApp message** — The flow spec says "CareRemind bot sends WhatsApp to doctor: Welcome Dr. Sharma!" after registration. Not implemented. |
| 11 | webhooks/router.py | **No UploadLog for WhatsApp uploads** — When doctor sends image/doc via WhatsApp, the pipeline runs but no `UploadLog` record is created (unlike dashboard uploads). |
| 12 | [api/client.ts](file:///c:/Users/sayan/DEVELOPEMENT/careremind/frontend/src/api/client.ts#L4) | `baseURL` hardcoded to `http://localhost:8000/api/v1`. No env variable. Will break in production. |
| 13 | api/client.ts | No 401 response interceptor — expired JWT silently fails, no redirect to login. |
| 14 | [middleware/auth.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/middleware/auth.py#L19-L27) | `PUBLIC_PATHS` missing: `/api/v1/auth/specialties`, all OAuth login/callback paths. Middleware logs will be noisy. |
| 15 | [App.tsx](file:///c:/Users/sayan/DEVELOPEMENT/careremind/frontend/src/App.tsx#L18) | Landing page at `/home` instead of `/`. Unauthenticated user visiting `/` gets Layout → redirected to `/login` instead of seeing landing page. |
| 16 | [Sidebar.tsx](file:///c:/Users/sayan/DEVELOPEMENT/careremind/frontend/src/components/Sidebar.tsx#L5-L11) | Missing nav links for `Settings`, `Billing`, `Staff` pages that exist in the `pages/` directory. |
| 17 | [Login.tsx](file:///c:/Users/sayan/DEVELOPEMENT/careremind/frontend/src/pages/Login.tsx#L29-L36) | **Registration missing whatsapp_number** — The flow spec requires doctor's personal WhatsApp number, but it's not collected in the registration form. |
| 18 | Login.tsx | **Registration missing language_preference** — The flow spec includes language preference, but it's not collected in the registration form. |
| 19 | [auth/schemas.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/auth/schemas.py#L9-L18) | **TenantRegister missing clinic address fields** — The flow spec includes optional clinic address (street, city, pincode, state), but schema doesn't have these fields. |
| 20 | [auth/models.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/auth/models.py#L17-L35) | **Tenant model missing clinic address columns** — No columns for street, city, pincode, state in the tenants table. |

### 🟡 P3 — Edge Cases Not Handled

| # | File | Issue |
|---|---|---|
| 21 | webhooks/router.py L238-244 | `_find_tenant_by_whatsapp`: compares `normalize_phone(sender)` against raw `Tenant.whatsapp_number`. If the stored number wasn't normalized on registration, lookup fails. |
| 22 | patients/router.py | No `DELETE /patients/{id}` endpoint. |
| 23 | reminders/router.py | No manual `POST /reminders/{id}/retry` endpoint. |
| 24 | webhooks/router.py L214-230 | `_download_media`: no httpx `timeout`. Could hang indefinitely if Meta API is slow. |
| 25 | scheduling.py L64 | `datetime.now()` — naive datetime. Should be `datetime.now(timezone.utc)` for consistent timezone comparison against `scheduled_at`. |
| 26 | docker-compose.prod.yml | No `healthcheck`, no `env_file`, no `depends_on`, no `volumes`. Services are bare. |
| 27 | Frontend | No `Dockerfile` for the restructured `frontend/` directory. |
| 28 | cache.py | Redis errors in `get()`/`set()` would crash dashboard endpoint. Should be wrapped in try/except with graceful fallback (only rate_limiter does this). |

---

## Proposed Changes

---

### Phase 1: Fix Dedup (P0 — Data Integrity)

#### [MODIFY] [patients/models.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/patients/models.py)
- Add `phone_hash = Column(String, nullable=False, index=True)` — stores deterministic HMAC-SHA256 hash of normalized phone for dedup.
- Keep existing `phone_encrypted` (Fernet) for actual decryption.

#### [MODIFY] [core/security.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/core/security.py)
- Add `hash_phone(phone: str) -> str` method to `EncryptionService` using HMAC-SHA256 with `FIELD_ENCRYPTION_KEY` as the key. Deterministic — same input always produces same output.
- Make `EncryptionService.__init__` **crash with `RuntimeError`** in production if `FIELD_ENCRYPTION_KEY` is empty. Dev auto-generation is fine but must be consistent across restarts (derive from a default dev key).

#### [MODIFY] [dedup_agent.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/agents/dedup_agent.py)
- Replace `encrypt()` lookup with `hash_phone()` for dedup comparison.
- Query: `WHERE phone_hash IN (...)` instead of `WHERE phone_encrypted IN (...)`.
- Still stash `_phone_encrypted` from `encrypt()` for the persistence node.

#### [MODIFY] [patients/service.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/patients/service.py)
- `create_patient()`: check duplicates via `phone_hash` instead of `phone_encrypted`.
- Every patient creation must set both `phone_hash` and `phone_encrypted`.

#### [MODIFY] [persistence.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/agents/nodes/persistence.py)
- Set `phone_hash` on each new Patient from `encryption_service.hash_phone(row["phone"])`.

#### [NEW] Alembic migration
- Add `phone_hash` column to `patients` table.
- Backfill: decrypt existing `phone_encrypted` → compute hash → store.

---

### Phase 2: Connect Reminder Scheduling to Ingestion (P0)

#### [MODIFY] [persistence.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/agents/nodes/persistence.py)
- After creating each Appointment, call `scheduling_graph.ainvoke()` to create Reminder records.
- Import the scheduling graph and the tenant model.
- Load the tenant from DB (or receive it from state).

#### [MODIFY] [graphs/ingestion.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/agents/graphs/ingestion.py)
- Add `tenant_id` → used by persistence node to fetch tenant for scheduling.

#### [MODIFY] [state.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/agents/state.py)
- Add `reminders_created: int` to IngestionState for tracking.

---

### Phase 3: Auth & Security Fixes (P1)

#### [MODIFY] [auth/router.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/auth/router.py)
- Make OAuth `redirect_uri` dynamic: `f"{settings.API_BASE_URL}/api/v1/auth/callback/google"`.
- Wrap OAuth callbacks in try/except: if `openid` is None or `openid.email` is None, return `HTTPException(400, "Email not provided by OAuth provider")`.

#### [MODIFY] [config.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/core/config.py)
- Add `API_BASE_URL: str = "http://localhost:8000"` for dynamic OAuth redirect URIs.

#### [MODIFY] [upload/router.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/upload/router.py)
- Fix line 70: `UploadStatus.COMPLETED.value` → `UploadStatus.COMPLETED` (consistency).

#### [MODIFY] [middleware/auth.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/middleware/auth.py)
- Add OAuth callback paths and `/api/v1/auth/specialties` to `PUBLIC_PATHS`.

#### [MODIFY] [scheduling.py nodes](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/agents/nodes/scheduling.py#L64)
- Fix `datetime.now()` → `datetime.now(timezone.utc)` for timezone-aware comparison.

---

### Phase 4: Missing V1 Workflow Steps (P2)

#### [MODIFY] [auth/service.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/auth/service.py)
- In `register_tenant()`: after creating tenant, fire a background WhatsApp welcome message to `data.whatsapp_number` (if provided) using `whatsapp_service`.

#### [MODIFY] [auth/service.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/auth/service.py)
- In `register_tenant()`: normalize `whatsapp_number` via `normalize_phone()` before saving.

#### [MODIFY] [auth/schemas.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/auth/schemas.py)
- Add to `TenantRegister`: `whatsapp_number: Optional[str]`, `language_preference: str = "english"`, `street: Optional[str]`, `city: Optional[str]`, `pincode: Optional[str]`, `state: Optional[str]`.

#### [MODIFY] [auth/models.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/auth/models.py)
- Add to `Tenant` model: `street: Column(String)`, `city: Column(String)`, `pincode: Column(String)`, `state: Column(String)`.

#### [MODIFY] [Login.tsx](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/frontend/src/pages/Login.tsx)
- Add input fields for `whatsapp_number` and `language_preference` (dropdown: English, Hindi, Tamil, Marathi, Bengali).
- Pass these fields to the registration API call.

#### [MODIFY] [webhooks/router.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/webhooks/router.py)
- In `_handle_whatsapp_image` and `_handle_whatsapp_document`: create an `UploadLog` record (like dashboard uploads do) for tracking.
- Add timeout to `_download_media`: `httpx.AsyncClient(timeout=30.0)`.

#### [MODIFY] [webhooks/router.py L238-244](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/webhooks/router.py#L233-L244)
- `_find_tenant_by_whatsapp`: also try matching without `+91` prefix in case stored numbers vary format.

---

### Phase 5: Frontend Fixes (P2)

#### [MODIFY] [api/client.ts](file:///c:/Users/sayan/DEVELOPEMENT/careremind/frontend/src/api/client.ts)
- `baseURL` → `import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'`.
- Add 401 response interceptor that clears localStorage and redirects to `/login`.

#### [MODIFY] [App.tsx](file:///c:/Users/sayan/DEVELOPEMENT/careremind/frontend/src/App.tsx)
- Fix routing: `/` = Landing page (unauthenticated) or redirect to `/dashboard` (authenticated).
- Add routes for `/settings`, `/billing`, `/staff`.

#### [MODIFY] [Sidebar.tsx](file:///c:/Users/sayan/DEVELOPEMENT/careremind/frontend/src/components/Sidebar.tsx)
- Add Settings and Billing nav links.

#### [NEW] [frontend/.env.example](file:///c:/Users/sayan/DEVELOPEMENT/careremind/frontend/.env.example)
- `VITE_API_URL=http://localhost:8000/api/v1`

#### [NEW] [frontend/Dockerfile](file:///c:/Users/sayan/DEVELOPEMENT/careremind/frontend/Dockerfile)
- Multi-stage build: `node:20-alpine` build stage → `nginx:alpine` serve stage.

---

### Phase 6: Docker / Deployment Hardening (P3)

#### [MODIFY] [docker-compose.yml](file:///c:/Users/sayan/DEVELOPEMENT/careremind/docker-compose.yml)
- Remove broken `nginx` service.
- Fix `prometheus` image to `prom/prometheus:latest`.
- Add `healthcheck` to Postgres and Redis.
- Add `depends_on` with `condition: service_healthy` for FastAPI and worker.

#### [MODIFY] [docker-compose.prod.yml](file:///c:/Users/sayan/DEVELOPEMENT/careremind/docker-compose.prod.yml)
- Add `env_file: .env` to all backend services.
- Add `healthcheck` blocks.
- Add `depends_on` chains.

---

### Phase 7: Backend Edge Cases (P3)

#### [MODIFY] [patients/router.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/patients/router.py)
- Add `DELETE /patients/{id}` with IDOR protection. Cascades delete appointments + reminders.

#### [MODIFY] [reminders/router.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/reminders/router.py)
- Add `POST /reminders/{id}/retry` to manually re-send a failed reminder.

#### [MODIFY] [dashboard/router.py](file:///c:/Users/sayan/DEVELOPEMENT/careremind/services/fastapi/app/features/dashboard/router.py)
- Wrap Redis cache calls in try/except so Redis being down doesn't crash the dashboard.

---

## Execution Order

```
Phase 1 (Dedup fix)        → highest impact, data integrity
Phase 2 (Reminder scheduling) → core workflow completion  
Phase 3 (Auth/Security)    → prevents runtime crashes
Phase 4 (Missing V1 steps) → welcome message, UploadLog, phone normalization
Phase 5 (Frontend)         → routing, auth guard, API URL
Phase 6 (Docker)           → deployment readiness
Phase 7 (Edge cases)       → polish
```

---

## Verification Plan

### After Each Phase
1. `pytest tests/` — all tests pass
2. Manual: FastAPI starts without import errors (`uvicorn app.main:app`)

### After All Phases
3. Register → JWT returned → profile accessible  
4. Upload Excel → patients created → reminders scheduled (check DB)
5. Upload Photo → OCR pipeline runs → unique patients only (no duplicates)
6. Upload same Excel again → 0 new patients (dedup works)
7. Hit `/dashboard/stats` → correct counts returned
8. `docker-compose up --build` → all services healthy
9. Check OAuth flows return proper error when secrets are empty

---

## Open Questions

> [!WARNING]
> **Alembic migration**: Adding `phone_hash` to the patients table requires a migration. If you have existing patient data in production, we need a backfill script that decrypts each `phone_encrypted` with the current key, computes the hash, and stores it. Do you have any existing data to worry about?

> [!NOTE]
> **Frontend stub pages**: `Settings.tsx`, `Billing.tsx`, `Staff.tsx`, `Onboarding.tsx` are 1-line placeholders. Should I build real V1 UIs for them, or leave as clean skeletons and focus on the critical backend fixes first?
