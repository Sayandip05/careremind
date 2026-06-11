# API Specifications & Developer Guide - CareRemind

**Version**: 1.1  
**Last Updated**: 2026-06-11  
**Status**: Production-Ready  
**Document Type**: REST API Reference & Integration Specifications

---

## 1. Authentication Protocol

The CareRemind API uses **JSON Web Token (JWT)** stateless authentication for all protected endpoints.

### Authentication Header
Every protected request must include the JWT token in the HTTP `Authorization` header:

```http
Authorization: Bearer <your_jwt_token_here>
```

- **JWT Expiry**: 24 hours from issuance.
- **Signing Algorithm**: HMAC-SHA256 (`HS256`).
- **Signature Secret**: `JWT_SECRET_KEY` (configured in environment).
- **Decrypted Payload Structure**:
  ```json
  {
    "sub": "tenant_id_uuid_string",
    "email": "doctor@example.com",
    "exp": 1781254399
  }
  ```

---

## 2. API Endpoint Index

| Category | Method | Path | Auth Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | `GET` | `/api/v1/auth/specialties` | No | List supported medical specialties |
| | `POST` | `/api/v1/auth/register` | No | Register a doctor tenant account |
| | `POST` | `/api/v1/auth/login` | No | Login and retrieve JWT access token |
| | `GET` | `/api/v1/auth/me` | Yes | Get active doctor tenant profile |
| | `PATCH` | `/api/v1/auth/me` | Yes | Update doctor tenant profile details |
| **Patients** | `GET` | `/api/v1/patients/` | Yes | Paginated list of doctor's patients |
| | `POST` | `/api/v1/patients/` | Yes | Create a new patient (encrypts phone) |
| | `GET` | `/api/v1/patients/{patient_id}` | Yes | Retrieve details of a specific patient |
| | `PATCH` | `/api/v1/patients/{patient_id}` | Yes | Update a specific patient's profile |
| | `DELETE` | `/api/v1/patients/{patient_id}`| Yes | Delete a patient and their history |
| **Appointments** | `GET` | `/api/v1/appointments/` | Yes | List doctor's appointments |
| | `POST` | `/api/v1/appointments/` | Yes | Create a new appointment & schedule reminders |
| **Reminders** | `GET` | `/api/v1/reminders/` | Yes | List scheduled or sent notifications |
| | `POST` | `/api/v1/reminders/{reminder_id}/retry` | Yes | Manually retry a failed reminder |
| **Uploads** | `POST` | `/api/v1/upload/excel` | Yes | Bulk ingest patients via spreadsheet |
| | `POST` | `/api/v1/upload/photo` | Yes | Upload register photo for OCR (Step 1) |
| | `POST` | `/api/v1/upload/photo/confirm` | Yes | Confirm reviewed OCR data to DB (Step 2) |
| **Clinics** | `GET` | `/api/v1/clinics/` | Yes | List multiple clinic locations |
| | `POST` | `/api/v1/clinics/` | Yes | Add a new clinic location |
| | `GET` | `/api/v1/clinics/{clinic_id}` | Yes | Retrieve specific clinic profile |
| | `PATCH` | `/api/v1/clinics/{clinic_id}` | Yes | Update a clinic's settings |
| | `DELETE` | `/api/v1/clinics/{clinic_id}` | Yes | Soft-delete a clinic location |
| **Bookings** | `GET` | `/api/v1/booking/clinics` | Yes | Get all active clinic locations |
| | `GET` | `/api/v1/booking/slots` | Yes | Get available slot timings for a clinic |
| | `POST` | `/api/v1/booking/reserve` | Yes | Lock a slot and create Razorpay order |
| | `POST` | `/api/v1/booking/confirm` | Yes | Confirm slot reservation via Razorpay sign |
| | `POST` | `/api/v1/booking/cancel` | Yes | Cancel an slot reservation |
| | `GET` | `/api/v1/booking/schedule/{schedule_date}`| Yes | Get daily schedule metadata |
| | `GET` | `/api/v1/booking/list` | Yes | Enriched confirmed bookings list for dashboard |
| | `GET` | `/api/v1/booking/download-pdf`| Yes | On-demand streaming download of daily PDF |
| | `GET` | `/api/v1/booking/my-bookings` | Yes | Get booking history for specific patient |
| **Billing** | `GET` | `/api/v1/billing/status` | Yes | Get active subscription plan status |
| | `GET` | `/api/v1/billing/history` | Yes | Get tenant subscription billing/invoice logs |
| **Dashboard** | `GET` | `/api/v1/dashboard/stats` | Yes | Fetch aggregates stats (cached 5 min) |
| **Contact** | `POST` | `/api/v1/contact/` | Yes | Submit client support message |
| **Audits** | `GET` | `/api/v1/audit/` | Yes | Fetch client operation logs |
| **Webhooks** | `GET` | `/api/v1/webhooks/whatsapp` | No | Meta webhook verification handshake |
| | `POST` | `/api/v1/webhooks/whatsapp` | No | Meta callback (STOP opt-out, file upload) |
| | `POST` | `/api/v1/webhooks/razorpay` | No | Razorpay webhook (payment.captured) |

---

## 3. Auth Features Endpoints

### 3.1 List Specialties
- **URL**: `/api/v1/auth/specialties`
- **Method**: `GET`
- **Auth**: None
- **Response** (`200 OK`):
  ```json
  [
    "General Medicine",
    "Dental",
    "Ophthalmology",
    "Orthopedic",
    "Pediatric",
    "Dermatology",
    "Diagnostic Lab",
    "Other"
  ]
  ```

### 3.2 Doctor Registration
- **URL**: `/api/v1/auth/register`
- **Method**: `POST`
- **Auth**: None
- **Request Body**:
  ```json
  {
    "doctor_name": "Dr. Arjun Mehta",
    "clinic_name": "City Health Clinic",
    "email": "doctor.arjun@example.com",
    "password": "StrongPassword123",
    "phone": "+919876543210",
    "specialty": "General Practice",
    "language_preference": "english"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer",
    "tenant_id": "c62bd0d3-35f9-4d2a-8bf8-2431718bf789",
    "doctor_name": "Dr. Arjun Mehta",
    "clinic_name": "City Health Clinic",
    "email": "doctor.arjun@example.com",
    "specialty": "General Practice",
    "plan": "free"
  }
  ```

### 3.3 Doctor Login
- **URL**: `/api/v1/auth/login`
- **Method**: `POST`
- **Auth**: None
- **Request Body** (Submitted as form-data per OAuth2 specifications):
  - `username`: `doctor.arjun@example.com`
  - `password`: `StrongPassword123`
- **Response** (`200 OK`):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer",
    "tenant_id": "c62bd0d3-35f9-4d2a-8bf8-2431718bf789",
    "doctor_name": "Dr. Arjun Mehta",
    "clinic_name": "City Health Clinic",
    "email": "doctor.arjun@example.com",
    "specialty": "General Practice",
    "plan": "free"
  }
  ```

### 3.4 Get Active Doctor Profile
- **URL**: `/api/v1/auth/me`
- **Method**: `GET`
- **Auth**: Required
- **Response** (`200 OK`):
  ```json
  {
    "id": "c62bd0d3-35f9-4d2a-8bf8-2431718bf789",
    "doctor_name": "Dr. Arjun Mehta",
    "clinic_name": "City Health Clinic",
    "email": "doctor.arjun@example.com",
    "phone": "+919876543210",
    "specialty": "General Practice",
    "language_preference": "english",
    "whatsapp_number": "+919876543210",
    "plan": "free",
    "is_active": true,
    "street": "12 Park Lane",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001"
  }
  ```

### 3.5 Update Doctor Profile
- **URL**: `/api/v1/auth/me`
- **Method**: `PATCH`
- **Auth**: Required
- **Request Body** (All fields optional):
  ```json
  {
    "doctor_name": "Dr. Arjun S. Mehta",
    "clinic_name": "City General Clinic",
    "street": "14 Park Lane"
  }
  ```
- **Response** (`200 OK`):
  (Returns updated doctor profile JSON representation).

---

## 4. Patient Features Endpoints

### 4.1 List Patients (Paginated)
- **URL**: `/api/v1/patients/`
- **Method**: `GET`
- **Auth**: Required
- **Query Parameters**:
  - `page`: `1` (default)
  - `per_page`: `20` (default, maximum `100`)
- **Response** (`200 OK`):
  ```json
  {
    "patients": [
      {
        "id": "a1d3f4b5-9012-4e56-9abc-def012345678",
        "name": "Karan Malhotra",
        "preferred_channel": "whatsapp",
        "language_preference": "hindi",
        "is_optout": false,
        "created_at": "2026-06-01T12:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 20
  }
  ```
  *(Note: Phone numbers are not returned in bulk lists for security)*.

### 4.2 Create Patient
- **URL**: `/api/v1/patients/`
- **Method**: `POST`
- **Auth**: Required
- **Request Body**:
  ```json
  {
    "name": "Karan Malhotra",
    "phone": "+919999988888",
    "preferred_channel": "whatsapp",
    "language_preference": "hindi"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "id": "a1d3f4b5-9012-4e56-9abc-def012345678",
    "name": "Karan Malhotra",
    "preferred_channel": "whatsapp",
    "language_preference": "hindi",
    "is_optout": false,
    "created_at": "2026-06-11T16:20:00Z"
  }
  ```
  *(Note: Phone number is encrypted with AES-256 Fernet and hashed with HMAC-SHA256 in DB)*.

---

## 5. Appointments Endpoints

### 5.1 Create Appointment & Schedule Reminders
- **URL**: `/api/v1/appointments/`
- **Method**: `POST`
- **Auth**: Required
- **Request Body**:
  ```json
  {
    "patient_id": "a1d3f4b5-9012-4e56-9abc-def012345678",
    "visit_date": "2026-06-11",
    "next_visit_date": "2026-07-11",
    "specialty_override": "Dental"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "id": "ef23b9d0-1234-5678-abcd-ef0123456789",
    "patient_id": "a1d3f4b5-9012-4e56-9abc-def012345678",
    "visit_date": "2026-06-11T00:00:00",
    "next_visit_date": "2026-07-11T00:00:00",
    "specialty_override": "Dental",
    "created_at": "2026-06-11T16:20:10Z"
  }
  ```
  *(Trigger Action: Evaluates timings via LangGraph Scheduling state machine and registers future reminder entries)*.

---

## 6. Reminders Endpoints

### 6.1 Force Retry Failed Reminder
- **URL**: `/api/v1/reminders/{reminder_id}/retry`
- **Method**: `POST`
- **Auth**: Required
- **Path Parameters**:
  - `reminder_id`: Target reminder UUID
- **Response** (`200 OK`):
  ```json
  {
    "message": "Reminder queued for retry",
    "reminder_id": "e981d012-5678-4321-abcd-ef0123456789",
    "status": "Pending"
  }
  ```
  *(Resets retry count, clears error logs, and flags status back to PENDING for the worker loop)*.

---

## 7. Upload Feature Endpoints

### 7.1 Bulk Upload Excel
- **URL**: `/api/v1/upload/excel`
- **Method**: `POST`
- **Auth**: Required
- **Request Payload** (`multipart/form-data`):
  - `file`: Raw binary of spreadsheet (.xlsx / .xls format, Max 10MB)
- **Response** (`200 OK`):
  ```json
  {
    "upload_id": "8902c34d-ef01-2345-6789-abcd01234567",
    "status": "completed",
    "filename": "patient_list.xlsx",
    "total_rows": 12,
    "new_patients": 10,
    "duplicates": 2,
    "skipped": 0,
    "errors": []
  }
  ```

### 7.2 Upload Register Photo for OCR Extraction (Step 1)
- **URL**: `/api/v1/upload/photo`
- **Method**: `POST`
- **Auth**: Required
- **Request Payload** (`multipart/form-data`):
  - `file`: Raw binary image file (Max 20MB)
- **Response** (`200 OK` - Returns extracted data for human confirmation):
  ```json
  {
    "upload_id": "f512b3d9-9abc-def0-1234-56789abcdef0",
    "status": "pending_review",
    "filename": "register_photo.jpg",
    "extracted_rows": [
      {
        "name": "Vikram Sen",
        "phone": "+919876500000",
        "visit_date": "2026-06-11",
        "next_visit_date": "2026-06-18"
      }
    ],
    "total_extracted": 1,
    "errors": [],
    "provider": "nvidia"
  }
  ```
  *(Note: This does not save anything to the database yet. It generates a temporary `UploadLog` in `PENDING_REVIEW` status)*.

### 7.3 Confirm Reviewed OCR Data (Step 2)
- **URL**: `/api/v1/upload/photo/confirm`
- **Method**: `POST`
- **Auth**: Required
- **Request Body**:
  ```json
  {
    "upload_id": "f512b3d9-9abc-def0-1234-56789abcdef0",
    "confirmed_rows": [
      {
        "name": "Vikram Sen",
        "phone": "+919876500000",
        "visit_date": "2026-06-11",
        "next_visit_date": "2026-06-18"
      }
    ]
  }
  ```
- **Response** (`200 OK` - commits entries to the database and schedules reminders):
  ```json
  {
    "upload_id": "f512b3d9-9abc-def0-1234-56789abcdef0",
    "status": "completed",
    "total_rows": 1,
    "new_patients": 1,
    "duplicates": 0,
    "skipped": 0,
    "errors": []
  }
  ```

---

## 8. Patient Booking Endpoints (Razorpay)

### 8.1 Fetch Available Timings
- **URL**: `/api/v1/booking/slots`
- **Method**: `GET`
- **Auth**: Required
- **Query Parameters**:
  - `clinic_location_id`: Clinic UUID
  - `booking_date`: Target date (`YYYY-MM-DD`, must be tomorrow or later)
- **Response** (`200 OK`):
  ```json
  [
    {
      "time": "09:00",
      "available": true
    },
    {
      "time": "09:30",
      "available": false
    }
  ]
  ```

### 8.2 Reserve Slot & Get Razorpay Order
- **URL**: `/api/v1/booking/reserve`
- **Method**: `POST`
- **Auth**: Required
- **Request Body**:
  ```json
  {
    "patient_id": "a1d3f4b5-9012-4e56-9abc-def012345678",
    "clinic_location_id": "90d12eef-1234-5678-9012-abcdef123456",
    "booking_date": "2026-06-12",
    "slot_time": "10:30:00"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "booking": {
      "id": "b0d1e2f3-4567-89ab-cdef-0123456789ab",
      "status": "Reserved",
      "amount": 200.00,
      "booking_date": "2026-06-12",
      "slot_time": "10:30:00"
    },
    "razorpay_order_id": "order_PJk123abcXYZ",
    "razorpay_key_id": "rzp_test_mockkey123",
    "amount": 200.00,
    "currency": "INR",
    "expires_in_seconds": 600
  }
  ```
  *(Hold Action: Locks the selected slot for 10 minutes. If unpaid, slot-cleanup cron cancels reservation)*.

### 8.3 Confirm Slot with Payment Signature
- **URL**: `/api/v1/booking/confirm`
- **Method**: `POST`
- **Auth**: Required
- **Request Body**:
  ```json
  {
    "booking_id": "b0d1e2f3-4567-89ab-cdef-0123456789ab",
    "razorpay_order_id": "order_PJk123abcXYZ",
    "razorpay_payment_id": "pay_PJk987defUVW",
    "razorpay_signature": "75390ebc1234a9b8..."
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "booking": {
      "id": "b0d1e2f3-4567-89ab-cdef-0123456789ab",
      "status": "Confirmed",
      "serial_number": 4,
      "amount": 200.00
    },
    "message": "Booking confirmed! Serial #4. See you on 12 June at 10:30 AM.",
    "pdf_bill_url": "https://supabase.co/storage/v1/object/public/bills/booking_b0d1e2f3.pdf"
  }
  ```
  *(Processes signature verify. On match, updates status to CONFIRMED, assigns a serial number, triggers ReportLab PDF builder, uploads PDF to storage, and sends a WhatsApp confirmation)*.

### 8.4 Enriched Dashboard Bookings List
- **URL**: `/api/v1/booking/list`
- **Method**: `GET`
- **Auth**: Required
- **Query Parameters**:
  - `booking_date`: Target date (`YYYY-MM-DD`, defaults to today)
  - `clinic_location_id`: Optional clinic filter UUID
- **Response** (`200 OK`):
  ```json
  [
    {
      "id": "b0d1e2f3-4567-89ab-cdef-0123456789ab",
      "serial_number": 4,
      "booking_date": "2026-06-12",
      "slot_time": "10:30",
      "slot_time_display": "10:30 AM",
      "patient_name": "Karan Malhotra",
      "clinic_name": "City Health Clinic",
      "clinic_address": "12 Park Lane, Mumbai",
      "clinic_location_id": "90d12eef-1234-5678-9012-abcdef123456",
      "status": "Confirmed",
      "payment_status": "Paid",
      "amount": 200.00,
      "confirmed_at": "2026-06-11T16:21:00Z"
    }
  ]
  ```

---

## 9. Webhook Ingestion Integrations

### 9.1 Meta WhatsApp Business Webhooks

#### A. Webhook Verification Handshake
- **URL**: `/api/v1/webhooks/whatsapp`
- **Method**: `GET`
- **Auth**: None
- **Query Parameters**:
  - `hub.mode`: `subscribe`
  - `hub.challenge`: `verification_random_challenge_string`
  - `hub.verify_token`: `HubVerificationSecretString` (configured in backend environment)
- **Response** (`200 OK`):
  Returns the raw string passed in `hub.challenge`.

#### B. Handle Incoming Messages (Callbacks)
- **URL**: `/api/v1/webhooks/whatsapp`
- **Method**: `POST`
- **Auth**: None (Verifies request payload validity dynamically)
- **Incoming Text Body Example**:
  ```json
  {
    "object": "whatsapp_business_account",
    "entry": [
      {
        "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
        "changes": [
          {
            "value": {
              "messaging_product": "whatsapp",
              "metadata": {
                "display_phone_number": "15550000000",
                "phone_number_id": "SENDER_PHONE_ID"
              },
              "contacts": [
                {
                  "profile": {
                    "name": "Karan Malhotra"
                  },
                  "wa_id": "919999988888"
                }
              ],
              "messages": [
                {
                  "from": "919999988888",
                  "id": "wamid.HBgLOTE5OTk5OTg4ODg4...",
                  "timestamp": "1781254890",
                  "text": {
                    "body": "STOP"
                  },
                  "type": "text"
                }
              ]
            },
            "field": "messages"
          }
        ]
      }
    ]
  }
  ```
  *Callback Operations based on webhook event:*
  - If text is `STOP` / `UNSUBSCRIBE`: patient linked to `919999988888` is updated to `is_optout = True`, and all pending scheduled reminders are cancelled.
  - If document / image attached: Downloads attachment and runs Ingestion pipeline.

### 9.2 Razorpay Webhook Ingestion
- **URL**: `/api/v1/webhooks/razorpay`
- **Method**: `POST`
- **Auth**: Signature Verification (Header check)
- **Request Headers**:
  - `X-Razorpay-Signature`: HMAC-SHA256 signature generated by Razorpay
- **Request Body**:
  ```json
  {
    "entity": "event",
    "account_id": "acc_mock_id",
    "event": "payment.captured",
    "contains": ["payment"],
    "payload": {
      "payment": {
        "entity": {
          "id": "pay_PJk987defUVW",
          "entity": "payment",
          "amount": 20000,
          "currency": "INR",
          "status": "captured",
          "order_id": "order_PJk123abcXYZ",
          "invoice_id": null,
          "international": false,
          "method": "upi",
          "amount_refunded": 0,
          "captured": true,
          "error_code": null,
          "error_description": null
        }
      }
    },
    "created_at": 1781254920
  }
  ```
  *(Validates incoming signatures. On match, handles booking confirmations if the client did not call `/confirm` on the frontend).*

---

## 10. API Errors Directory

| Status Code | Error Detail (JSON response) | Cause |
| :--- | :--- | :--- |
| `400 Bad Request` | `{"detail": "Only .xlsx and .xls files accepted"}` | Excel file extension mismatch |
| | `{"detail": "Invalid payment signature"}` | Razorpay validation signature mismatch |
| `401 Unauthorized` | `{"detail": "Not authenticated"}` | Missing or malformed JWT token |
| | `{"detail": "Token has expired"}` | Token payload `exp` timestamp is in the past |
| `403 Forbidden` | `{"detail": "Access denied"}` | Tenant ID mismatch (IDOR attempt caught) |
| `404 Not Found` | `{"detail": "Patient not found"}` | Patient record doesn't exist under tenant context |
| `409 Conflict` | `{"detail": "Slot no longer available or invalid date"}`| Time slot is already booked or reserved |
| `429 Too Many Requests`| `{"detail": "Too Many Requests. Please slow down."}`| Exceeded rate limiter threshold bucket |
| `500 Internal Error` | `{"detail": "An internal error occurred."}` | Uncaught server exception |
