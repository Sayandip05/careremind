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
| `payments` | Payment records | tenant_id FK |
| `bookings` | Patient bookings (V2) | tenant_id FK, patient_id FK, appointment_id FK |
| `daily_schedules` | Generated PDFs (V2) | tenant_id FK, clinic_location_id FK |

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

### Patient Self-Booking Flow (V2)

```mermaid
sequenceDiagram
    participant P as Patient
    participant W as WhatsApp
    participant A as FastAPI
    participant R as Razorpay
    participant DB as PostgreSQL
    participant PDF as PDF Generator

    P->>W: Receives reminder with "Want to book your next visit?" button
    P->>W: Taps button
    W->>A: Webhook: button_click event
    A->>DB: Fetch patient, clinic locations
    A-->>W: Show clinic locations (if multiple)
    P->>W: Selects clinic
    W->>A: GET /booking/slots?clinic_id=...&date=tomorrow
    A->>DB: Fetch available slots for tomorrow
    DB-->>A: slots[] (9 AM, 10 AM, 11 AM...)
    A-->>W: Show available slots
    P->>W: Selects 10 AM slot
    W->>A: POST /booking/reserve (slot_time=10:00)
    A->>DB: Create booking (status=reserved, expires in 10 min)
    A->>R: Create payment order (₹200)
    R-->>A: order_id, payment_link
    A-->>W: Payment link (in-chat)
    P->>R: Completes payment
    R->>A: POST /webhooks/razorpay (payment success)
    A->>DB: Update booking (status=confirmed, payment_id)
    A->>DB: Assign serial_number (next available for that day)
    A->>PDF: Generate patient bill PDF
    A-->>W: "✅ Booking confirmed! Serial #5. See you tomorrow at 10 AM."
    A->>W: Send PDF bill to patient
    
    Note over A,DB: At midnight (12:00 AM) — Daily Schedule Generation
    A->>DB: Fetch all confirmed bookings for today
    A->>PDF: Generate daily schedule PDF
    Note over PDF: Online bookings at top (Serial #1, #2, #3...)<br/>Walk-in slots at bottom (10 slots reserved)
    A->>DB: Save DailySchedule record with PDF URL
    A->>W: Send daily schedule PDF to doctor's WhatsApp
    
    Note over P,W: Next morning
    Doctor->>Receptionist: Hands printed PDF
    Receptionist->>P: Calls "Serial #5" when ready
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

### Booking (V2)
| Scenario | Handling |
|----------|----------|
| Same-day booking attempt | Return 400, "Only next-day booking allowed" |
| Slot already taken | Return 409, "Slot no longer available" |
| Payment timeout (>10 min) | Cancel reservation, free slot |
| Payment failed | Cancel reservation, notify patient |
| No slots available | Show "All slots full, try walk-in" |
| Booking after 11:59 PM | Return 400, "Booking closed for tomorrow" |

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
