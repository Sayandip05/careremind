# Phase 3: Ingestion Pipeline — Walkthrough

> **Session:** 2026-03-07  
> **Scope:** Excel upload + Photo OCR + Dedup + Full pipeline  
> **Files changed:** 12 files (2 new, 9 modified, 1 deleted)

---

## Data Flow

```
POST /upload/excel or /upload/photo
  ↓ save file to Supabase Storage
  ↓ create upload_log (status=processing)
  ↓ Orchestrator.process()
  │   ├── Excel → ExcelAgent (openpyxl) → extract rows
  │   └── Photo → OcrAgent (GPT-4o Mini vision) → extract rows
  ↓ phone_formatter.normalize() each row
  ↓ DedupAgent.deduplicate() → split new vs existing
  ↓ Save new Patient + Appointment to DB
  ↓ update upload_log (status=completed, counts)
  ↓ Return summary
```

---

## What Was Built

### Utilities (3 files)

| File | What It Does |
|------|-------------|
| [phone_formatter.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/utils/phone_formatter.py) | Strips non-digits, handles +91/0/091 prefixes, validates 10-digit starting with 6-9 |
| [date_parser.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/utils/date_parser.py) | 10+ Indian date formats, Excel datetime objects, serial numbers, month names |
| [excel_validator.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/utils/excel_validator.py) | Regex-based fuzzy column matching: "Contact No" → phone, "Patient Name" → name |

### Agents (4 files)

| File | What It Does |
|------|-------------|
| [excel_agent.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/agents/excel_agent.py) | Reads .xlsx via openpyxl, auto-detects headers, maps columns, extracts structured rows |
| [ocr_agent.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/agents/ocr_agent.py) | Sends base64 image to GPT-4o Mini vision, parses JSON response into structured rows |
| [dedup_agent.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/agents/dedup_agent.py) | Encrypts phones, batch-fetches existing from DB, splits new vs duplicate |
| [orchestrator.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/agents/orchestrator.py) | Routes file type → correct agent → dedup → saves patients + appointments |

### Services (2 files)

| File | What It Does |
|------|-------------|
| [openai_service.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/openai_service.py) | OpenAI GPT-4o Mini wrapper with chat + vision support (replaces groq_service) |
| [storage.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/storage.py) | Supabase Storage upload via REST API with local fallback |

### Routes (1 file)

| File | Endpoints |
|------|-----------|
| [upload.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/api/v1/upload.py) | `POST /upload/excel`, `POST /upload/photo` — auth-protected, full pipeline |

### Cleanup
- **Deleted** [groq_service.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/groq_service.py) — replaced by [openai_service.py](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/services/openai_service.py)

---

## Design Decisions

| Decision | Why |
|----------|-----|
| **GPT-4o Mini** over Google Vision | User preference — single API for both OCR + structured extraction |
| **Fuzzy column matching** | Indian clinic spreadsheets have inconsistent headers |
| **Batch dedup** | One DB query for all rows instead of N queries per row |
| **Pre-encrypted phones in DedupAgent** | Reused by Orchestrator when saving → avoids double encryption |
| **Local storage fallback** | Works in dev without Supabase Storage bucket configured |

---

## Verification

| Step | Result |
|------|--------|
| Server starts clean | ✅ |
| GET /health → 200 | ✅ |
| Full pipeline wired (no import errors) | ✅ |
| End-to-end test with Excel | ⏳ Needs JWT token |

---

## What's Next

To fully test the pipeline you need:
1. **A JWT token** — create a tenant in Supabase, then generate a token via [create_access_token()](file:///c:/Users/sayan/AI%20ML/careremind/services/fastapi/app/core/security.py#16-29)
2. **A test Excel file** — with columns: Name, Phone, Next Visit Date
3. **An OpenAI API key** — for photo OCR testing
