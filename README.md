# CareRemind 🏥

**AI-powered appointment reminder system for Indian doctors via WhatsApp & SMS**

---

## Problem It Solves

Indian doctors face **30-40% no-show rates** due to patients forgetting appointments. CareRemind automates personalized reminders via WhatsApp/SMS, reducing no-shows and improving clinic efficiency. Doctors can upload patient data via Excel, photos (OCR), or WhatsApp, and the system handles everything automatically.

---

## 🚀 Live Demo

**Frontend**: [https://careremind.vercel.app](https://careremind.vercel.app)  
**API Docs**: [https://careremind-api.onrender.com/docs](https://careremind-api.onrender.com/docs)

---

## 📸 Screenshots

> *Add screenshot or demo GIF here*

---

## 🛠️ Tech Stack

**Backend**:
- FastAPI (Python 3.11+)
- PostgreSQL (Supabase)
- Redis (Upstash)
- Celery (Background jobs)
- LangGraph (AI workflows)

**Frontend**:
- React + TypeScript
- Vite
- TailwindCSS
- Zustand (State management)

**AI & Integrations**:
- OpenAI GPT-4o Mini (OCR)
- NVIDIA NIM (Vision)
- WhatsApp Business API (Meta)
- Fast2SMS (Fallback)
- Razorpay (Payments)

**Infrastructure**:
- Docker + Docker Compose
- Render (Backend hosting)
- Vercel (Frontend hosting)
- Supabase (Database + Storage)
- Caddy (Reverse proxy)

---

## ✨ Key Features

- 📤 **3 Upload Options**: Dashboard (Excel/Photo) or WhatsApp (send photos directly)
- 🤖 **AI-Powered OCR**: Extract patient data from handwritten registers using GPT-4o Mini
- 📱 **Smart Reminders**: Specialty-based timing (7-day, 30-day follow-ups) via WhatsApp/SMS
- 📅 **Online Booking**: Patients book appointments via web link with Razorpay payment
- 🏥 **Multi-Clinic Support**: Doctors can manage multiple clinic locations
- 🔒 **Security First**: AES-256 encryption, Argon2 password hashing, JWT authentication
- 📊 **Real-Time Dashboard**: Track reminders, bookings, and patient stats
- 🔄 **Auto-Retry**: Failed reminders automatically retry with exponential backoff

---

## 🚀 Quick Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- PostgreSQL (or use Supabase)
- Redis (or use Upstash)

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/careremind.git
cd careremind

# Copy environment file
cp .env.example .env
# Edit .env with your credentials (Supabase, Redis, etc.)

# Start all services
docker-compose up

# Run migrations (in another terminal)
docker-compose exec api alembic upgrade head

# Access services
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend**:
```bash
cd services/fastapi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../../.env.example ../../.env
# Edit .env with your credentials

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with API URL

# Start dev server
npm run dev
```

**Celery Worker** (optional, for background jobs):
```bash
cd services/fastapi
celery -A app.worker.celery_app worker --loglevel=info
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CAREREMIND SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────────────────────┐ │
│  │   React      │◄────────┤   FastAPI Backend            │ │
│  │   Frontend   │  HTTPS  │   (Async + APScheduler)      │ │
│  │   (Vite)     │         │                              │ │
│  └──────────────┘         └──────────┬───────────────────┘ │
│                                       │                      │
│                    ┌──────────────────┼──────────────┐      │
│                    │                  │              │      │
│            ┌───────▼────┐  ┌──────────▼──────┐  ┌───▼────┐│
│            │ PostgreSQL │  │    Redis        │  │Supabase││
│            │ (Supabase) │  │ (Cache/Queue)   │  │(Storage││
│            └────────────┘  └─────────────────┘  └────────┘│
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         CELERY WORKERS (Background Jobs)             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  EXTERNAL: WhatsApp │ SMS │ Razorpay │ OpenAI       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Architecture Style**: Modular Monolith (single codebase, multiple containers)

---

## 📚 Documentation

Comprehensive documentation available in `/docs`:

- **[HLD.md](docs/HLD.md)**: High-Level Design (system overview, data flows, C4 diagrams)
- **[LLD.md](docs/LLD.md)**: Low-Level Design (database schema, API endpoints, algorithms)
- **[system-architecture.md](docs/system-architecture.md)**: Detailed architecture (flows, integrations, security)
- **[deployment.md](docs/deployment.md)**: Deployment guide (Render, Vercel, environment setup)
- **[cost-scaling-analysis.md](docs/cost-scaling-analysis.md)**: Cost analysis & scaling strategy

---

## 🔑 Environment Variables

Required variables (see `.env.example` for complete list):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_URL=https://...
SUPABASE_KEY=...

# Cache & Queue
REDIS_URL=redis://...

# Authentication
JWT_SECRET_KEY=...
FIELD_ENCRYPTION_KEY=...

# Optional (for full features)
META_WHATSAPP_TOKEN=...
FAST2SMS_API_KEY=...
OPENAI_API_KEY=...
RAZORPAY_KEY_ID=...
```

Generate encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 🧪 Testing

```bash
cd services/fastapi

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

---

## 📊 Project Structure

```
careremind/
├── services/
│   └── fastapi/              # Backend API
│       ├── app/
│       │   ├── agents/       # LangGraph AI workflows
│       │   ├── core/         # Security, database, config
│       │   ├── features/     # Feature modules (auth, patients, etc.)
│       │   ├── scheduler/    # APScheduler jobs
│       │   └── worker/       # Celery tasks
│       ├── alembic/          # Database migrations
│       └── tests/            # Unit & integration tests
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   └── store/            # Zustand state
│   └── dist/                 # Build output
├── docs/                     # Documentation
├── scripts/                  # Setup scripts
├── docker-compose.yml        # Development setup
└── .env.example              # Environment template
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Sayan Dey**

- LinkedIn: [linkedin.com/in/yourusername](https://linkedin.com/in/yourusername)
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - AI workflow orchestration
- [Supabase](https://supabase.com/) - Open-source Firebase alternative
- [Render](https://render.com/) - Cloud hosting platform
- [Vercel](https://vercel.com/) - Frontend deployment platform

---

## 📈 Roadmap

- [ ] Multi-language support (Hindi, Tamil, Telugu)
- [ ] Voice reminders via phone calls
- [ ] Patient mobile app (React Native)
- [ ] Analytics dashboard with charts
- [ ] Integration with clinic management systems
- [ ] Automated follow-up surveys
- [ ] Prescription reminders

---

## 💡 Support

If you find this project helpful, please ⭐ star the repository!

For issues or questions, please [open an issue](https://github.com/yourusername/careremind/issues).

---

**Made with ❤️ for Indian healthcare**
