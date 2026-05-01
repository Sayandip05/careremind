# Low-Level Design (LLD) - CareRemind

**Version**: 1.0  
**Last Updated**: 2026-05-01

---

## Database Schema

### Tables Overview (10 tables)

```
tenants (doctors)
├── patients
│   ├── appointments
│   │   ├── reminders
│   │   └── bookings
│   └── bookings
├── clinic_locations
│   ├── bookings
│   └── daily_schedules
├── upload_logs
└── audit_logs
```

---

### 1. tenants (Doctors)
```sql
id                  STRING PRIMARY KEY (UUID)
doctor_name         STRING NOT NULL
clinic_name         STRING NOT NULL
email               STRING UNIQUE NOT NULL (indexed)
phone               STRING
specialty           STRING
language_preference STRING DEFAULT 'english'
whatsapp_number     STRING
hashed_password     STRING NOT NULL (Argon2)
plan                ENUM(free, pro, enterprise) DEFAULT 'free'
is_active           BOOLEAN DEFAULT true
street, city, pincode, state  STRING (clinic address)
created_at, updated_at  TIMESTAMP
```

**Indexes**: `email`  
**Relationships**: 1-to-many with patients, appointments, reminders, upload_logs, clinic_locations, bookings

---

### 2. patients
```sql
id                  STRING PRIMARY KEY (UUID)
tenant_id           STRING FK(tenants.id) ON DELETE CASCADE (indexed)
name                STRING NOT NULL
phone_encrypted     STRING NOT NULL (AES-256 Fernet)
phone_hash          STRING NOT NULL (HMAC-SHA256, indexed for dedup)
preferred_channel   ENUM(whatsapp, sms, both) DEFAULT 'whatsapp'
has_whatsapp        BOOLEAN DEFAULT false
language_preference STRING
is_optout           BOOLEAN DEFAULT false
created_at, updated_at  TIMESTAMP
```

**Indexes**: `tenant_id`, `phone_hash`  
**Unique**: None (allows duplicates across tenants)  
**Encryption**: `phone_encrypted` (non-deterministic), `phone_hash` (deterministic for dedup)

---

### 3. appointments
```sql
id                  STRING PRIMARY KEY (UUID)
tenant_id           STRING FK(tenants.id) ON DELETE CASCADE (indexed)
patient_id          STRING FK(patients.id) ON DELETE CASCADE (indexed)
visit_date          DATE NOT NULL
next_visit_date     DATE
specialty_override  STRING (overrides tenant.specialty)
notes_encrypted     TEXT (AES-256)
source              ENUM(excel, photo, manual) DEFAULT 'manual'
created_at          TIMESTAMP
```

**Indexes**: `tenant_id`, `patient_id`

---

### 4. reminders
```sql
id                  STRING PRIMARY KEY (UUID)
tenant_id           STRING FK(tenants.id) ON DELETE CASCADE (indexed)
patient_id          STRING FK(patients.id) ON DELETE CASCADE (indexed)
appointment_id      STRING FK(appointments.id) ON DELETE CASCADE (indexed)
reminder_number     INTEGER DEFAULT 1
status              ENUM(Pending, Sent, Failed, Confirmed, Cancelled, Optout) DEFAULT 'Pending'
message_text        TEXT
language_used       STRING
channel             STRING (whatsapp/sms)
scheduled_at        TIMESTAMP NOT NULL
sent_at             TIMESTAMP
error_log           TEXT
retry_count         INTEGER DEFAULT 0
created_at, updated_at  TIMESTAMP
```

**Indexes**: `tenant_id`, `patient_id`, `appointment_id`  
**Query Pattern**: `WHERE status='Pending' AND scheduled_at <= NOW()`

---

### 5. bookings
```sql
id                  STRING PRIMARY KEY (UUID)
tenant_id           STRING FK(tenants.id) ON DELETE CASCADE (indexed)
patient_id          STRING FK(patients.id) ON DELETE CASCADE (indexed)
appointment_id      STRING FK(appointments.id) ON DELETE SET NULL
clinic_location_id  STRING FK(clinic_locations.id) ON DELETE CASCADE (indexed)
booking_date        DATE NOT NULL (indexed)
slot_time           TIME NOT NULL
serial_number       INTEGER (assigned at midnight)
status              STRING DEFAULT 'reserved' (indexed)
payment_status      STRING DEFAULT 'pending'
amount              NUMERIC(10,2) DEFAULT 200.00
razorpay_order_id   STRING
razorpay_payment_id STRING
reserved_at         TIMESTAMP DEFAULT NOW()
confirmed_at        TIMESTAMP
expires_at          TIMESTAMP (reserved_at + 10 minutes)
completed_at        TIMESTAMP
created_at, updated_at  TIMESTAMP
```

**Indexes**: `tenant_id`, `patient_id`, `clinic_location_id`, `booking_date`, `status`  
**Unique Constraint**: Partial unique index on `(clinic_location_id, booking_date, slot_time)` WHERE `status IN ('reserved', 'confirmed')` - prevents double-booking

---

### 6. clinic_locations
```sql
id                  STRING PRIMARY KEY (UUID)
tenant_id           STRING FK(tenants.id) ON DELETE CASCADE (indexed)
clinic_name         STRING NOT NULL (e.g., "Morning Clinic")
address_line        STRING NOT NULL
city                STRING NOT NULL
pincode             STRING(6) NOT NULL
state               STRING
phone               STRING
is_active           BOOLEAN DEFAULT true
created_at, updated_at  TIMESTAMP
```

**Indexes**: `tenant_id`  
**Purpose**: Supports doctors with multiple clinic locations

---

### 7. daily_schedules
```sql
id                  STRING PRIMARY KEY (UUID)
tenant_id           STRING FK(tenants.id) ON DELETE CASCADE (indexed)
clinic_location_id  STRING FK(clinic_locations.id) ON DELETE CASCADE (indexed)
schedule_date       DATE NOT NULL (indexed)
pdf_url             STRING
total_online_bookings  INTEGER DEFAULT 0
total_walk_in_slots    INTEGER DEFAULT 10
generated_at        TIMESTAMP
sent_at             TIMESTAMP
created_at          TIMESTAMP
```

**Indexes**: `tenant_id`, `clinic_location_id`, `schedule_date`  
**Generated**: Midnight job creates PDF and sends to doctor's WhatsApp

---

### 8. upload_logs
```sql
id                  STRING PRIMARY KEY (UUID)
tenant_id           STRING FK(tenants.id) ON DELETE CASCADE (indexed)
filename            STRING NOT NULL
file_type           STRING NOT NULL (excel/photo)
total_rows          INTEGER DEFAULT 0
duplicates_skipped  INTEGER DEFAULT 0
failed_rows         INTEGER DEFAULT 0
status              ENUM(processing, completed, failed, partial) DEFAULT 'processing'
storage_url         STRING
created_at          TIMESTAMP
```

**Indexes**: `tenant_id`

---

### 9. audit_logs
```sql
id                  STRING PRIMARY KEY (UUID)
tenant_id           STRING FK(tenants.id) ON DELETE SET NULL
user_id             STRING
action              STRING NOT NULL (create/update/delete)
resource            STRING NOT NULL (table name)
resource_id         STRING
ip_address          STRING
user_agent          STRING
old_value           JSONB (PostgreSQL) / JSON (SQLite)
new_value           JSONB / JSON
created_at          TIMESTAMP
```

**Append-Only**: Never deleted, used for compliance

---

## API Endpoints (40 endpoints)

### Auth (`/api/v1/auth`)
```
GET    /specialties              List available specialties
POST   /register                 Register new doctor
POST   /login                    Login (email + password)
GET    /me                       Get current user profile
PATCH  /me                       Update profile
GET    /login/google             OAuth Google login
GET    /callback/google          OAuth Google callback
GET    /login/facebook           OAuth Facebook login
GET    /callback/facebook        OAuth Facebook callback
```

### Patients (`/api/v1/patients`)
```
GET    /                         List patients (paginated)
POST   /                         Create patient manually
GET    /{patient_id}             Get patient details
PATCH  /{patient_id}             Update patient
DELETE /{patient_id}             Delete patient
```

### Appointments (`/api/v1/appointments`)
```
GET    /                         List appointments (filter by patient)
POST   /                         Create appointment manually
```

### Reminders (`/api/v1/reminders`)
```
GET    /                         List reminders (filter by status)
POST   /{reminder_id}/retry      Retry failed reminder
```

### Upload (`/api/v1/upload`)
```
POST   /excel                    Upload Excel file
POST   /photo                    Upload photo (OCR)
```

### Booking (`/api/v1/booking`)
```
GET    /clinics                  List doctor's clinic locations
GET    /slots                    Get available slots (date + clinic)
POST   /reserve                  Reserve slot (10-min hold)
POST   /confirm                  Confirm booking (after payment)
POST   /cancel                   Cancel booking
GET    /schedule/{date}          Get daily schedule PDF
GET    /my-bookings              List patient's bookings
```

### Clinics (`/api/v1/clinics`)
```
GET    /                         List clinic locations
POST   /                         Create clinic location
GET    /{clinic_id}              Get clinic details
PATCH  /{clinic_id}              Update clinic
DELETE /{clinic_id}              Delete clinic
```

### Dashboard (`/api/v1/dashboard`)
```
GET    /stats                    Get dashboard statistics
```

### Billing (`/api/v1/billing`)
```
GET    /history                  Payment history
GET    /status                   Subscription status
```

### Audit (`/api/v1/audit`)
```
GET    /                         Get audit logs (filtered)
```

### Webhooks (`/api/v1/webhooks`)
```
GET    /whatsapp                 WhatsApp verification (Meta)
POST   /whatsapp                 WhatsApp incoming messages
POST   /razorpay                 Razorpay payment webhook
```

### Contact (`/api/v1/contact`)
```
POST   /                         Submit contact form
```

---

## Key Algorithms

### 1. Phone Deduplication
**Problem**: Prevent duplicate patients across uploads

**Algorithm**:
```python
# Step 1: Normalize phone
phone = "+919876543210"
normalized = phone.strip().replace(" ", "").replace("-", "")

# Step 2: Create deterministic hash (HMAC-SHA256)
phone_hash = HMAC(FIELD_ENCRYPTION_KEY, normalized, SHA256)
# Result: "a3f5b2c1..." (always same for same phone)

# Step 3: Check if hash exists in database
existing = db.query(Patient).filter(
    Patient.tenant_id == tenant_id,
    Patient.phone_hash == phone_hash
).first()

if existing:
    skip_duplicate()
else:
    # Step 4: Encrypt phone for storage (non-deterministic)
    phone_encrypted = Fernet(FIELD_ENCRYPTION_KEY).encrypt(phone)
    # Result: "gAAAABf..." (different each time)
    
    # Step 5: Save both
    patient = Patient(
        phone_encrypted=phone_encrypted,  # For retrieval
        phone_hash=phone_hash              # For dedup
    )
    db.add(patient)
```

**Why Two Fields?**
- `phone_hash`: Deterministic (same input → same output) for dedup lookups
- `phone_encrypted`: Non-deterministic (secure storage, can be decrypted)

**Time Complexity**: O(1) - Hash lookup with index

---

### 2. Specialty-Based Reminder Scheduling
**Problem**: Different specialties need different reminder timings

**Algorithm**:
```python
# Step 1: Get specialty
specialty = get_specialty(tenant.specialty or "general")

# Step 2: Get timing rules
timings = specialty.get_reminder_timing()
# Example for Dentist:
# [
#   ReminderTiming(days_before=7, time="09:00", label="7-day"),
#   ReminderTiming(days_before=30, time="09:00", label="30-day")
# ]

# Step 3: Calculate scheduled_at for each timing
for timing in timings:
    scheduled_at = timing.get_scheduled_at(visit_date)
    # visit_date = 2026-05-15
    # 7-day: 2026-05-08 09:00
    # 30-day: 2026-04-15 09:00
    
    # Step 4: Skip if in past
    if scheduled_at < now():
        continue
    
    # Step 5: Check for duplicate
    existing = db.query(Reminder).filter(
        Reminder.appointment_id == appointment_id,
        Reminder.scheduled_at == scheduled_at
    ).first()
    
    if not existing:
        reminder = Reminder(
            appointment_id=appointment_id,
            scheduled_at=scheduled_at,
            status="Pending"
        )
        db.add(reminder)
```

**Specialty Rules**:
- Dentist: 7-day, 30-day
- Cardiologist: 7-day, 30-day
- Dermatologist: 7-day, 30-day
- General: 7-day, 30-day

**Time Complexity**: O(n) where n = number of timings (typically 2)

---

### 3. Booking Slot Race Condition Prevention
**Problem**: Two patients book same slot simultaneously

**Algorithm**:
```python
# Database constraint (PostgreSQL partial unique index)
CREATE UNIQUE INDEX idx_unique_active_slot
ON bookings (clinic_location_id, booking_date, slot_time)
WHERE status IN ('reserved', 'confirmed');

# Application logic
try:
    booking = Booking(
        clinic_location_id=clinic_id,
        booking_date=date,
        slot_time=time,
        status='reserved',
        expires_at=now() + 10 minutes
    )
    db.add(booking)
    db.flush()  # Triggers constraint check
    
    return booking  # Success
    
except IntegrityError:
    # Race condition: Another user booked this slot
    db.rollback()
    return None  # Slot unavailable
```

**Why Partial Index?**
- Only prevents duplicates for `reserved` and `confirmed` statuses
- Allows multiple `cancelled` or `completed` bookings for same slot
- Database-level guarantee (not just application logic)

**Time Complexity**: O(1) - Index lookup

---

### 4. Reservation Expiry Cleanup
**Problem**: Reserved slots expire after 10 minutes if not paid

**Algorithm**:
```python
# Scheduled job (every 5 minutes)
def cleanup_expired_reservations():
    now = datetime.now(timezone.utc)
    
    # Find expired reservations
    expired = db.query(Booking).filter(
        Booking.status == 'reserved',
        Booking.expires_at < now
    ).all()
    
    # Mark as expired
    for booking in expired:
        booking.status = 'expired'
    
    db.commit()
    
    return len(expired)
```

**Time Complexity**: O(n) where n = number of expired bookings

---

### 5. Serial Number Assignment
**Problem**: Assign sequential numbers to confirmed bookings at midnight

**Algorithm**:
```python
# Midnight job (00:00 IST)
def assign_serial_numbers(clinic_id, date):
    # Get all confirmed bookings for tomorrow
    bookings = db.query(Booking).filter(
        Booking.clinic_location_id == clinic_id,
        Booking.booking_date == date,
        Booking.status == 'confirmed',
        Booking.serial_number == None
    ).order_by(Booking.confirmed_at).all()
    
    # Assign sequential numbers
    for idx, booking in enumerate(bookings, start=1):
        booking.serial_number = idx
    
    db.commit()
    
    return len(bookings)
```

**Time Complexity**: O(n log n) - Sort by confirmed_at

---

## Design Patterns

### 1. Repository Pattern
**Location**: `app/features/*/service.py`

**Why**: Separates business logic from data access

```python
# Bad: Business logic in route
@router.post("/booking")
async def create_booking(data, db):
    booking = Booking(**data)
    db.add(booking)
    db.commit()
    return booking

# Good: Business logic in service
@router.post("/booking")
async def create_booking(data, db):
    return await BookingService.reserve_slot(db, **data)
```

---

### 2. Dependency Injection
**Location**: `app/core/security.py`, `app/core/database.py`

**Why**: Testable, reusable, follows FastAPI conventions

```python
# Inject database session
async def get_db():
    async with async_session_maker() as session:
        yield session

# Inject current user
async def get_current_tenant(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Tenant:
    # Verify token, load user
    return tenant

# Use in routes
@router.get("/patients")
async def list_patients(
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    # tenant and db are automatically injected
    pass
```

---

### 3. State Machine (LangGraph)
**Location**: `app/agents/graphs/*.py`

**Why**: Complex workflows with branching logic

```python
# Ingestion Graph
graph = StateGraph(IngestionState)
graph.add_node("route", route_node)
graph.add_node("extract", extract_node)
graph.add_node("dedup", deduplicate_node)
graph.add_node("save", save_node)

graph.add_edge("route", "extract")
graph.add_edge("extract", "dedup")
graph.add_edge("dedup", "save")

# Execute
result = await graph.invoke({"file_type": "excel", ...})
```

---

### 4. Strategy Pattern
**Location**: `app/specialty.py`

**Why**: Different specialties have different reminder rules

```python
class Specialty(ABC):
    @abstractmethod
    def get_reminder_timing(self) -> List[ReminderTiming]:
        pass

class DentistSpecialty(Specialty):
    def get_reminder_timing(self):
        return [
            ReminderTiming(days_before=7, time="09:00"),
            ReminderTiming(days_before=30, time="09:00")
        ]

# Usage
specialty = get_specialty("dentist")
timings = specialty.get_reminder_timing()
```

---

### 5. Singleton Pattern
**Location**: `app/core/integrations/*.py`

**Why**: Reuse HTTP clients, avoid connection leaks

```python
class WhatsAppService:
    _http_client: Optional[httpx.AsyncClient] = None
    
    def set_http_client(self, client: httpx.AsyncClient):
        self._http_client = client
    
    async def send_message(self, to, message):
        # Reuse shared client
        await self._http_client.post(...)

# Initialize once in main.py
whatsapp_service.set_http_client(app.state.http_client)
```

---

## Edge Cases Handled

### 1. Double-Booking Prevention
**Problem**: Two users book same slot simultaneously

**Solution**: Database partial unique constraint + IntegrityError handling

---

### 2. Reservation Expiry
**Problem**: User reserves slot but doesn't pay

**Solution**: 10-minute expiry + scheduled cleanup job every 5 minutes

---

### 3. Phone Number Deduplication
**Problem**: Same patient uploaded multiple times

**Solution**: HMAC-SHA256 hash for deterministic dedup lookup

---

### 4. Past Reminder Skipping
**Problem**: Upload old appointments, reminders already passed

**Solution**: Skip reminders where `scheduled_at < now()`

---

### 5. Opt-Out Handling
**Problem**: Patient sends "STOP" to WhatsApp

**Solution**: Mark `patient.is_optout = True`, cancel all pending reminders

---

### 6. Payment Signature Verification
**Problem**: Fake payment confirmation

**Solution**: Verify Razorpay signature with HMAC-SHA256

```python
expected = HMAC(razorpay_secret, order_id + "|" + payment_id, SHA256)
if expected != signature:
    raise HTTPException(400, "Invalid signature")
```

---

### 7. Multi-Tenant Isolation
**Problem**: Doctor A sees Doctor B's patients

**Solution**: Every query filtered by `tenant_id`

```python
patients = db.query(Patient).filter(
    Patient.tenant_id == current_tenant.id
).all()
```

---

### 8. Cold Start Handling
**Problem**: Render free tier has 30s cold starts

**Solution**: Health check endpoint + cron job pings every 10 minutes

---

### 9. Missing Encryption Key
**Problem**: FIELD_ENCRYPTION_KEY not set in dev

**Solution**: Auto-generate fixed dev key (never in production)

```python
if not settings.FIELD_ENCRYPTION_KEY:
    if settings.is_production:
        raise RuntimeError("Encryption key required in production")
    else:
        # Use fixed dev key for consistency
        key = b"dev-careremind-key-do-not-use-in-prod="
```

---

### 10. WhatsApp/SMS Fallback
**Problem**: WhatsApp API fails

**Solution**: Automatic fallback to SMS with retry logic

```python
try:
    await whatsapp_service.send_message(phone, message)
except Exception:
    await sms_service.send_message(phone, message)
```

---

## Component Diagram (C4 Level 3)

```
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Layer (FastAPI Routes)                          │  │
│  │  - auth/router.py                                    │  │
│  │  - patients/router.py                                │  │
│  │  - appointments/router.py                            │  │
│  │  - reminders/router.py                               │  │
│  │  - booking/router.py                                 │  │
│  │  - upload/router.py                                  │  │
│  │  - webhooks/router.py                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Service Layer (Business Logic)                      │  │
│  │  - BookingService (slot management)                  │  │
│  │  - Orchestrator (AI pipeline)                        │  │
│  │  - Integration Services (WhatsApp, SMS, Razorpay)    │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Agent Layer (LangGraph State Machines)              │  │
│  │  - Ingestion Graph (route → extract → dedup → save) │  │
│  │  - Scheduling Graph (specialty → timings → create)  │  │
│  │  - Notification Graph (load → check → send)         │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Layer (SQLAlchemy Models)                      │  │
│  │  - Tenant, Patient, Appointment, Reminder, Booking   │  │
│  │  - ClinicLocation, DailySchedule, UploadLog          │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Core Layer (Shared Utilities)                       │  │
│  │  - security.py (JWT, encryption, auth)               │  │
│  │  - database.py (connection pool)                     │  │
│  │  - config.py (environment variables)                 │  │
│  │  - storage.py (Supabase file uploads)                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-05-01
