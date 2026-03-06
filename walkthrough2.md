# Phase 2: Auth + CRUD Routes — Walkthrough

> **Session:** 2026-03-07  
> **Scope:** Service layer + production API routes with IDOR protection  
> **Files changed:** 11 files (2 new, 8 modified, 1 deleted)

---

## What Was Done

### 1. Service Layer (3 files)

| File | What It Does |
|------|-------------|
| [patient_service.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/patient_service.py) | [create](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/api/v1/patients.py#44-60) (encrypt phone + dedup check), [list](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/patient_service.py#53-81) (paginated), [get](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/database.py#28-40) (IDOR check), [update](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/patient_service.py#106-133) (IDOR + re-encrypt) |
| [appointment_service.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/appointment_service.py) | [create](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/api/v1/patients.py#44-60) (verify patient ownership before insert), [list](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/patient_service.py#53-81) (paginated + patient filter) |
| [tenant_service.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/tenant_service.py) | [get_profile](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/tenant_service.py#13-16), [update_profile](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/tenant_service.py#18-46) (partial updates) |

### 2. API Routes (6 files)

| Route | Endpoints | Auth | IDOR Protected |
|-------|-----------|------|----------------|
| [auth.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/api/v1/auth.py) | `GET /auth/me`, `PATCH /auth/me` | ✅ | N/A (own data) |
| [patients.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/api/v1/patients.py) | `GET /patients`, `POST /patients`, `GET /patients/{id}`, `PATCH /patients/{id}` | ✅ | ✅ on get/update |
| [appointments.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/api/v1/appointments.py) | `GET /appointments`, `POST /appointments` | ✅ | ✅ on create |
| [dashboard.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/api/v1/dashboard.py) | `GET /dashboard/stats` | ✅ | N/A |
| [reminders.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/api/v1/reminders.py) | `GET /reminders?status=Pending` | ✅ | N/A |
| [router.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/api/v1/router.py) | Added [auth](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/exceptions.py#18-23) and [appointments](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/appointment_service.py#54-87) routers | — | — |

### 3. Cleanup

- **Deleted** [encryption_service.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/encryption_service.py) — redundant wrapper around `security.encryption_service`
- **Fixed** [services/__init__.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/__init__.py) — removed eager imports causing circular dependency

---

## Security: IDOR Protection

Every route that receives a user-supplied ID verifies tenant ownership:

```python
# The golden rule — applied everywhere
patient = await db.get(Patient, patient_id)
if str(patient.tenant_id) != str(tenant_id):
    raise ForbiddenException("Patient does not belong to your account")
```

| Route | What's Checked |
|-------|---------------|
| `GET /patients/{id}` | patient.tenant_id == JWT tenant_id |
| `PATCH /patients/{id}` | patient.tenant_id == JWT tenant_id |
| `POST /appointments` | patient_id in body → belongs to JWT tenant |

---

## Dashboard: Single Query

Stats are fetched in **one DB round-trip** using `count + filter`:

```python
select(
    func.count(distinct(Patient.id)).filter(...).label("total_patients"),
    func.count(distinct(Reminder.id)).filter(status == PENDING).label("pending"),
    func.count(distinct(Reminder.id)).filter(status == SENT).label("sent"),
    ...
)
```

---

## Verification Results

| Step | Test | Result |
|------|------|--------|
| 1 | uvicorn starts without errors | ✅ |
| 2 | `GET /health` returns 200 | ✅ `{"status":"healthy"}` |
| 3 | `GET /auth/me` without token returns 403 | ✅ `{"detail":"Not authenticated"}` |
| 4-8 | Full CRUD flow | ⏳ Needs Supabase connection + JWT |

---

## What's Next

1. **Connect Supabase** — run the SQL migration, update `.env` with real credentials
2. **Test Steps 4-8** — full CRUD flow with real database
3. **Phase 3** — Excel upload agent + photo OCR agent
