# CareRemind

AI-powered patient appointment reminder system for Indian clinics.

---

## Quick Start

```bash
# Clone
git clone https://github.com/yourorg/careremind.git
cd careremind

# Setup
cp .env.example .env
# Edit .env with your credentials

# Run locally
docker-compose up -d

# Access
# API: http://localhost:8000
# Dashboard: http://localhost:3000
# Landing: http://localhost:3002
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI + Python 3.11 |
| Frontend | React 18 + TypeScript + Vite |
| Database | PostgreSQL (Supabase) |
| Queue | Redis + Celery |
| Scheduler | APScheduler |
| AI | LangGraph + GroQ/OpenAI |

---

## Project Structure

```
services/
├── fastapi/           # Main API (modular monolith)
│   └── app/
│       ├── features/  # Domain modules
│       ├── agents/    # AI pipelines
│       ├── core/      # Shared infrastructure
│       ├── middleware/
│       └── specialty/
├── worker/           # Celery background tasks
└── scheduler/        # Cron jobs (APScheduler)
frontend/
├── dashboard/        # Doctor dashboard
└── landing/          # Marketing site
```

---

## Features

- **WhatsApp Bot Upload**: Doctor sends photo/Excel to bot — data extracted automatically
- **Patient Management**: CRUD with phone encryption (AES-256)
- **Multi-Clinic Support**: One doctor, multiple clinic locations (structured addresses)
- **Automated Reminders**: WhatsApp + SMS at 7/30 days after visit
- **Multi-language**: Hindi, English, Tamil, Marathi, Bengali
- **7 Specialties**: General, Pediatric, Orthopedic, Eye, Dental, Skin, Diagnosis
- **Dashboard**: Read-only monitoring — stats, patients, reminder history
- **V2 (Upcoming)**: Patient self-booking via WhatsApp with priority queue + midnight PDF

---

## Environment Variables

See `.env.example` for required variables.

---

## Contributing

1. Create feature branch
2. Write tests
3. Submit PR

---

## License

MIT
