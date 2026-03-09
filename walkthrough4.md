# Phase 4: Reminder Engine — Walkthrough

> **Session:** 2026-03-09  
> **Scope:** Specialty timing, multilingual messages, WhatsApp/SMS sending  
> **Files changed:** 22 files (2 new, 19 modified, 1 folder deleted)

---

## Architecture

```
Appointment created
  → ReminderAgent.schedule_reminders()
       → Specialty.get_reminder_timing() → [1-day, 2-hour, etc.]
       → Creates Reminder records with scheduled_at

When scheduler fires (Phase 5):
  → NotificationService.send_reminder()
       → MessageAgent.generate() → template + optional AI polish
       → WhatsAppService → Meta Cloud API
       └── Failed? → SMSService → Fast2SMS
       → Update Reminder (sent/failed/optout)

Patient replies STOP:
  → Webhook → _handle_optout() → is_optout=True, cancel pending reminders
```

---

## What Was Built

### Specialty System (9 files)

| Specialty | Timing | Pre-visit | Tone | Follow-up |
|-----------|--------|-----------|------|-----------|
| General | 1 day | Bring prescriptions | neutral | 30 days |
| Dental | 2 days + 2 hrs | Don't eat 2 hrs before | caring | 180 days |
| Eye | 1 day | Bring driver | calm | 90 days |
| Orthopedic | 2 days | Wear loose clothes | supportive | 45 days |
| Pediatric | 1 day + 2 hrs | Bring vaccination card | friendly | 30 days |
| Skin | 1 day | No creams/makeup | gentle | 14 days |
| Diagnosis | 1 day | 12hr fast for blood test | precise | 90 days |

Registry: [specialty/__init__.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/specialty/__init__.py) — [get_specialty("dental")](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/specialty/__init__.py#34-42) with aliases

### Language Templates (8 files)

5 languages with reminder templates: **English, Hindi, Bengali, Marathi, Tamil**

Registry: [detector.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/languages/detector.py) — [get_language("hi")](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/languages/detector.py#30-38) with aliases

### Agents (2 files)

| File | What It Does |
|------|-------------|
| [reminder_agent.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/agents/reminder_agent.py) | Creates Reminder records from appointment + specialty timing. Skips past dates and duplicates |
| [message_agent.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/agents/message_agent.py) | Fills language template, optionally polishes with GPT-4o Mini |

### Services (3 files)

| File | What It Does |
|------|-------------|
| [whatsapp_service.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/whatsapp_service.py) | Meta Cloud API v21.0, error handling, privacy logging |
| [sms_service.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/sms_service.py) | Fast2SMS with unicode support (Hindi/Bengali/Tamil) |
| [notification_service.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/notification_service.py) | WhatsApp first → SMS fallback → status tracking |

### Webhook (1 file)

| File | What It Does |
|------|-------------|
| [webhooks.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/api/v1/webhooks.py) | Meta webhook verification + STOP opt-out (marks patient, cancels reminders) |

### Cleanup
- **Deleted** `services/whatsapp/` — entire Node.js folder (replaced by Python)
- **Fixed** ReminderAgent + NotificationService — removed non-existent `patient_id` column reference

---

## Verification

| Step | Result |
|------|--------|
| Server starts clean | ✅ |
| GET /health → 200 | ✅ |
| No import errors | ✅ |
| Full pipeline wired | ✅ |

---

## What's Next

**Phase 5: Background Jobs** — Celery worker + scheduler to trigger reminders daily at 9 AM
