# CareRemind V2 — Future Implementation

> **V1 = Solo doctor** (one login, one clinic, their patients)  
> **V2 = Multi-doctor clinics, hospitals, chains**

---

## V1 → V2: What Changes

| Aspect | V1 (Current) | V2 (Future) |
|--------|-------------|-------------|
| Users | 1 doctor = 1 tenant | Multiple doctors + receptionists per clinic |
| Login | Doctor logs in directly | Role-based login (doctor / receptionist / admin) |
| Data access | Everything belongs to one doctor | Shared patient data within a clinic |
| Billing | Per-doctor plan | Per-clinic plan with seat pricing |
| Dashboard | Solo doctor stats | Clinic-wide stats + per-doctor breakdown |

---

## V2 Feature Roadmap

### 1. Role-Based Access Control (RBAC)
**Current:** One doctor = one tenant  
**V2:** Multiple users per tenant with roles

```
Tenant (Clinic)
├── Doctor (can see own patients, send reminders)
├── Receptionist (can upload data, view patients, NOT billing)
└── Admin (everything + staff management + billing)
```

**Implementation:**
- New `User` model (separate from `Tenant`)
- `Tenant` becomes the clinic entity
- `User.role` field: `doctor | receptionist | admin`
- `User.tenant_id` links to clinic
- Replace `get_current_tenant` with `get_current_user` + role checks
- Route-level permission decorators

---

### 2. Multi-Doctor Patient Sharing
**Current:** Patients belong to one doctor  
**V2:** Patients belong to a clinic, visible to all authorized staff

**Changes:**
- Patient queries filter by `tenant_id` (clinic) not individual doctor
- Appointment has `doctor_id` field (which doctor saw the patient)
- Reminders link to specific doctor for personalized messages
- Audit trail shows which staff member performed each action

---

### 3. Clinic-Wide Dashboard
**Current:** Solo doctor dashboard  
**V2:** Admin sees clinic-wide view, doctors see their own view

**New dashboard features:**
- Total patients across all doctors
- Per-doctor reminder stats
- Staff activity log
- Revenue per doctor (if billing per consultation)

---

### 4. Elasticsearch for Patient Search (#23)
**Why V2:** With thousands of patients across doctors, PostgreSQL `LIKE` queries become slow

**Implementation:**
- Index patients in Elasticsearch on create/update
- Full-text search endpoint: `GET /patients/search?q=john`
- Fuzzy matching for misspelled names
- Filter by doctor, date range, specialty

---

### 5. Advanced Billing (Razorpay Integration)
**Current:** Payment model exists but no actual payment flow  
**V2:** Full subscription management

**Features:**
- Razorpay checkout for plan upgrades (Free → Pro → Enterprise)
- Webhook for payment confirmation
- Auto-downgrade on payment failure
- Usage-based billing (per-SMS charges)
- Invoice generation (PDF)

---

### 6. Multi-Clinic Chain Support
**For hospital chains with multiple branches:**
- Parent-child tenant structure
- Cross-clinic patient transfer
- Central admin dashboard for all branches
- Unified billing per chain

---

### 7. Mobile App (React Native)
- Doctor app for viewing reminders on the go
- Push notifications for daily summary
- Quick patient lookup by phone number
- Offline mode for areas with poor connectivity

---

### 8. Advanced AI Features
- **Smart scheduling:** AI suggests optimal follow-up times based on diagnosis
- **Patient risk scoring:** Predict likelihood of no-show based on history
- **Voice notes:** Doctor records voice → AI transcribes → saves as appointment notes
- **Sarvam AI integration:** Regional language STT for patient data entry

---

### 9. Analytics & Reports
- Monthly trend charts (patients added, reminders sent)
- Specialty-wise patient distribution
- Best time to send reminders (based on delivery rate data)
- Exportable PDF/Excel reports for clinic records

---

### 10. Compliance & Audit
- HIPAA-like compliance logging
- Data retention policies per regulation
- Patient consent management
- Right to deletion (GDPR-style)
- Encrypted backups

---

### 11. Direct Appointment Booking System (Patient-Facing)
**Current:** Only doctors interact with the platform  
**V2:** Patients can book appointments directly

**User Flow:**
```
Patient opens booking page
  → Searches doctor by name or specialty
  → Sees which clinics the doctor visits (with address, timings, fees)
  → Picks the nearest clinic & available time slot
  → Pays via Razorpay (consultation fee)
  → Gets Booking ID + Payment Receipt PDF (email + WhatsApp)

Doctor side:
  → Gets notified of new booking
  → Booking appears in dashboard with auto-generated Booking ID + PDF
  → Daily summary PDF generated at 9 PM with next day's appointments
```

**Backend:**
- `Booking` model: `id`, `patient_id`, `doctor_id`, `clinic_id`, `slot_datetime`, `status`, `payment_id`
- `ClinicSchedule` model: which doctor visits which clinic on which days/times
- `POST /bookings` — create booking + trigger payment
- `GET /bookings?date=...` — doctor's appointments for a date
- `POST /bookings/{id}/confirm` — mark as confirmed after payment webhook
- `GET /bookings/{id}/receipt` — download PDF receipt

**PDF Generation:**
- Patient receipt: Booking ID, doctor name, clinic address, date/time, amount paid
- Doctor daily sheet: all bookings for the next day, generated nightly via Celery task
- Use **ReportLab** or **WeasyPrint** for PDF generation

**Payment Flow:**
```
Patient selects slot → Razorpay checkout → payment_id saved
  → Razorpay webhook confirms → booking status = "confirmed"
  → PDF receipt generated → sent via WhatsApp + email
```

**Frontend:**
- `/book` public page (no login needed for patients)
- Doctor search + clinic picker + slot calendar
- Razorpay checkout embed
- Booking confirmation page with downloadable PDF

---

## V2 Tech Additions

| Technology | Purpose |
|-----------|---------|
| **Elasticsearch** | Fast patient search at scale |
| **Razorpay** | Payment processing + booking payments |
| **React Native** | Mobile app |
| **Sentry** | Error tracking in production |
| **AWS SES / Resend** | Transactional emails at scale |
| **CloudFront CDN** | Static asset delivery |
| **GitHub Actions CI/CD** | Automated testing + deployment |
| **Kubernetes** | Container orchestration for scaling |
| **ReportLab / WeasyPrint** | PDF generation (receipts, daily sheets) |
