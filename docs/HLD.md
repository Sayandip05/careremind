# High-Level Design

## Vision

AI-powered patient appointment reminder system for Indian clinics. Doctors upload patient data (Excel/Photo), system automatically sends WhatsApp/SMS reminders at optimal times.

---

## User Journeys

### Doctor Registration (Onboarding)
1. Doctor visits landing page
2. Clicks "Get Started"
3. Fills registration form: name, clinic name, specialty, WhatsApp number, language preference
4. Adds clinic location(s): clinic_name + address_line + city + pincode (optional, multiple allowed)
5. CareRemind WhatsApp bot number sent to doctor on WhatsApp
6. Doctor saves bot number — onboarding complete
7. Dashboard available for monitoring (read-only for daily work)

### Patient Import — WhatsApp Bot (Primary, Daily)
1. End of clinic day — doctor clicks photo of patient register
2. Sends photo OR Excel file directly to CareRemind WhatsApp bot
3. Bot identifies doctor by their registered WhatsApp number
4. Bot runs: OcrAgent/ExcelAgent → DedupAgent → saves patients + appointments
5. Bot replies with summary: "✅ 12 patients added, 3 duplicates skipped"
6. Doctor spends ~30 seconds. Done.

### Patient Import — Dashboard (Optional/Secondary)
1. Doctor or staff opens dashboard
2. Navigates to Upload page
3. Drags Excel file or photo
4. System processes same pipeline
5. Results displayed on dashboard

### Reminder Delivery
1. Scheduler triggers at 9:00 AM IST daily
2. System fetches pending reminders
3. MessageAgent generates localized message
4. WhatsApp sent first, SMS fallback on failure
5. Status updated in database

### Patient Self-Booking
1. Patient receives WhatsApp reminder
2. Clicks link to booking page
3. Selects available slot
4. Confirmation sent to doctor and patient

---

## API List

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new doctor |
| POST | `/api/v1/auth/login` | Login, get JWT |
| GET | `/api/v1/auth/me` | Get current profile |
| PATCH | `/api/v1/auth/me` | Update profile |

### Patients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/patients` | List patients (paginated) |
| POST | `/api/v1/patients` | Create patient |
| GET | `/api/v1/patients/{id}` | Get patient |
| PATCH | `/api/v1/patients/{id}` | Update patient |

### Appointments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/appointments` | List appointments |
| POST | `/api/v1/appointments` | Create appointment |

### Reminders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/reminders` | List reminders (filterable) |

### Upload
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload/excel` | Upload Excel |
| POST | `/api/v1/upload/photo` | Upload photo |

### Billing
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/billing/history` | Payment history |
| GET | `/api/v1/billing/status` | Subscription status |

### Staff
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/staff` | List staff |
| GET | `/api/v1/staff/{id}` | Get staff details |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/stats` | Aggregated statistics |

### Audit
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/audit` | Activity logs |

### Webhooks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/webhooks/whatsapp` | WhatsApp events |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/health/ready` | Readiness check (DB) |

---

## Major Entities

### Tenant (Doctor)
- id, email, phone, clinic_name, doctor_name
- specialty, language_preference, whatsapp_number
- plan (free/trial/paid), is_active
- hashed_password

### ClinicLocation
- id, tenant_id
- clinic_name (e.g. "City Clinic", "Morning Clinic")
- address_line, city, pincode
- is_active
- Note: One doctor can have multiple clinic locations
- Note: Doctor manages via dashboard (add/delete/update)
- Note: Patient selects clinic during V2 booking

### Patient
- id, tenant_id, name
- phone_encrypted (AES-256)
- preferred_channel (whatsapp/sms)
- language_preference

### Appointment
- id, tenant_id, patient_id
- visit_date, appointment_type
- notes

### Reminder
- id, tenant_id, patient_id, appointment_id
- scheduled_at, status (pending/sent/failed)
- channel_used, sent_at, error_log
- retry_count

### UploadLog
- id, tenant_id, filename
- file_type (excel/photo)
- storage_url, status
- total_rows, duplicates_skipped, failed_rows

### Staff
- id, tenant_id, name, role
- phone, email, is_active

### Payment
- id, tenant_id, amount, currency
- status, razorpay_payment_id
- created_at

### AuditLog
- id, tenant_id, user_id
- action, resource, resource_id
- metadata, created_at

---

## Non-Functional Requirements

### Performance
- API response time: <200ms (p95)
- Dashboard stats: <500ms
- File upload (10MB Excel): <30s

### Availability
- 99.5% uptime target
- Health checks for all services
- Graceful degradation on failures

### Security
- All API calls authenticated (except public paths)
- Patient PII encrypted at rest
- JWT tokens expire in 24h
- IDOR protection on all resources

### Scalability
- Support 1000+ patients per doctor
- Handle 100 concurrent uploads
- Queue 10,000 pending reminders

### Multi-Language
- UI: Hindi, English
- Messages: Hindi, English, Tamil, Marathi, Bengali
- Specialty-specific timing rules
