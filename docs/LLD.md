# Low-Level Design

## Database Schema

### Entity Relationship

```mermaid
erDiagram
    Tenant ||--o{ Patient : has
    Tenant ||--o{ Appointment : has
    Tenant ||--o{ Reminder : has
    Tenant ||--o{ UploadLog : has
    Tenant ||--o{ AuditLog : has
    Tenant ||--o{ Staff : has
    Tenant ||--o{ Payment : has
    Tenant ||--o{ ClinicLocation : has
    Patient ||--o{ Appointment : has
    Appointment ||--o{ Reminder : has
```

### Tables

| Table | Purpose | Key Constraints |
|-------|---------|-----------------|
| `tenants` | Doctor accounts | email UNIQUE |
| `clinic_locations` | Doctor clinic addresses | tenant_id FK, multiple per tenant |
| `patients` | Patient records | tenant_id FK, phone_encrypted UNIQUE per tenant |
| `appointments` | Visit records | tenant_id FK, patient_id FK |
| `reminders` | Scheduled notifications | tenant_id FK, appointment_id FK |
| `upload_logs` | Upload history | tenant_id FK |
| `audit_logs` | Activity tracking | tenant_id FK |
| `staff` | Staff members | tenant_id FK |
| `payments` | Payment records | tenant_id FK |

### ClinicLocation Schema

```sql
CREATE TABLE clinic_locations (
    id           VARCHAR PRIMARY KEY,
    tenant_id    VARCHAR NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    clinic_name  VARCHAR NOT NULL,
    address_line VARCHAR NOT NULL,
    city         VARCHAR NOT NULL,
    pincode      VARCHAR(6) NOT NULL,
    is_active    BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
-- One doctor -> many clinic locations
-- Managed by doctor from dashboard (add/delete/update)
-- Patient selects clinic during V2 booking
```

---

## Sequence Diagrams

### Upload Flow — WhatsApp Bot (Primary, Daily)

```mermaid
sequenceDiagram
    participant Dr as Doctor (WhatsApp)
    participant W as WhatsApp Webhook
    participant A as FastAPI
    participant O as Orchestrator
    participant E as ExcelAgent / OcrAgent
    participant Ded as DedupAgent
    participant DB as PostgreSQL

    Dr->>W: Sends photo or Excel to CareRemind bot
    W->>A: POST /webhooks/whatsapp (file payload)
    A->>A: Identify tenant by sender WhatsApp number
    A->>O: Process file
    O->>E: Extract rows
    E-->>O: extracted_rows[]
    O->>Ded: Deduplicate
    Ded-->>O: new_rows[], duplicates[]
    O->>DB: Save new patients + appointments
    O->>DB: Create reminders (7d, 30d)
    O-->>A: result
    A->>Dr: "✅ 12 added, 3 duplicates skipped" (WhatsApp reply)
```

### Upload Flow — Dashboard (Secondary/Optional)

```mermaid
sequenceDiagram
    participant D as Dashboard
    participant A as FastAPI
    participant O as Orchestrator
    participant E as ExcelAgent
    participant Dedupe as DedupAgent
    participant DB as PostgreSQL
    participant S as Supabase Storage

    D->>A: POST /upload/excel (file)
    A->>S: Save file to storage
    A->>O: Process file (excel)
    O->>E: Extract rows
    E-->>O: extracted_rows[]
    O->>Dedupe: Deduplicate
    Dedupe-->>O: new_rows[], duplicates[]
    O->>DB: Save new patients + appointments
    DB-->>O: saved
    O->>DB: Create reminders (7d, 30d)
    O-->>A: result
    A-->>D: success response
```

### Reminder Delivery Flow

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant C as Celery Worker
    participant M as MessageAgent
    participant N as NotificationService
    participant W as WhatsApp API
    participant SMS as Fast2SMS
    participant DB as PostgreSQL

    S->>C: Trigger daily job (9AM IST)
    C->>DB: Fetch pending reminders
    DB-->>C: reminders[]
    loop For each reminder
        C->>M: Generate message
        M-->>C: localized_message
        C->>N: Send reminder
        alt WhatsApp available
            N->>W: Send WhatsApp
            W-->>N: success/fail
        else WhatsApp failed
            N->>SMS: Send SMS fallback
            SMS-->>N: success/fail
        end
        C->>DB: Update reminder status
    end
```

### Auth Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as FastAPI
    participant DB as PostgreSQL
    participant JWT as JWT Service

    U->>A: POST /auth/login (email, password)
    A->>DB: Find tenant by email
    DB-->>A: tenant
    A->>JWT: Verify password (bcrypt)
    JWT-->>A: valid
    A->>JWT: Create JWT (tenant_id, email, exp)
    JWT-->>A: access_token
    A-->>U: {access_token, tenant_id}
    
    U->>A: GET /patients (Authorization: Bearer token)
    A->>JWT: Verify token
    JWT-->>A: payload (tenant_id)
    A->>DB: Fetch patients WHERE tenant_id=payload.tenant_id
    DB-->>A: patients[]
    A-->>U: patients list
```

---

## Edge Cases

### Upload
| Scenario | Handling |
|----------|----------|
| Empty Excel | Return 400, "No data found in file" |
| Invalid phone format | Skip row, add to errors list |
| Duplicate phone | Skip row, mark as duplicate |
| Very large file (>10MB) | Return 400, "File too large" |
| Wrong file type | Return 400, "Only .xlsx accepted" |
| OCR fails | Mark as failed, log error |

### Reminders
| Scenario | Handling |
|----------|----------|
| Patient opted out | Skip, mark as Optout |
| WhatsApp not on phone | Fallback to SMS |
| Network failure | Retry up to 2 times |
| Phone invalid | Mark as Failed, log error |
| Duplicate reminder | Prevented by unique constraint |

### Auth
| Scenario | Handling |
|----------|----------|
| Invalid credentials | 401, "Invalid email or password" |
| Expired token | 401, "Token expired" |
| Inactive account | 401, "Account deactivated" |
| Missing token | 403, "Authorization required" |

---

## Error Handling

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation) |
| 401 | Unauthorized (auth failure) |
| 403 | Forbidden (no permission) |
| 404 | Not Found |
| 422 | Unprocessable Entity (Pydantic) |
| 429 | Rate Limited |
| 500 | Internal Server Error |

### Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

### Logging

- All errors logged with traceback
- Production: hide details, show generic message
- Development: show full error for debugging

---

## Security

### Encryption
- Patient phone numbers: AES-256 (Fernet)
- Field-level, not column-level

### Authentication
- JWT with 24h expiry
- Bearer token in Authorization header

### Authorization
- Tenant ID in JWT payload
- All queries filter by tenant_id
- IDOR protection on single-resource endpoints

---

## API Patterns

### Pagination
```python
GET /patients?page=1&per_page=20
```

Response:
```json
{
  "patients": [...],
  "total": 150,
  "page": 1,
  "per_page": 20
}
```

### Filtering
```python
GET /reminders?status=Pending
GET /audit?resource=patient&resource_id=abc
```

### IDOR Protection
Every GET/PATCH/DELETE on single resource:
```python
# Verify resource belongs to requesting tenant
if str(resource.tenant_id) != str(tenant.id):
    raise ForbiddenException()
```
