# Deployment Guide

## Docker Compose (Local Development)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f fastapi

# Stop all services
docker-compose down
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| caddy | 80, 443 | Reverse proxy with automatic HTTPS |
| fastapi | 8000 | API server (includes APScheduler) |
| worker | - | Celery background tasks (optional) |
| dashboard | 3000 | React doctor dashboard |
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis (queue + cache) |

---

## Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/careremind

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Redis
REDIS_URL=redis://redis:6379/0

# Auth
JWT_SECRET_KEY=your-secure-secret-min-32-chars
FIELD_ENCRYPTION_KEY=your-fernet-key

# AI
GROQ_API_KEY=your-groq-key
OPENAI_API_KEY=your-openai-key

# WhatsApp (Optional — for production with real Meta Business account)
META_WHATSAPP_TOKEN=
META_PHONE_NUMBER_ID=

# SMS
FAST2SMS_API_KEY=your-fast2sms-key

# Vision
VISION_BACKEND=nvidia
NVIDIA_API_KEY=your-nvidia-key

# App
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000

# App
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:3002
```

## Deployment Tiers

CareRemind supports two distinct deployment tiers, depending on whether you are deploying for a portfolio/resume or as a real startup.

### Tier 1: Free Tier Deployment (Resume/Portfolio)
*Focus: Zero-cost deployment to showcase skills, using all free tiers. Suitable for ~50 test users.*

**Infrastructure:**
- **Backend (FastAPI, Celery, Scheduler):** Host on **Render (Free Tier)** or **Railway (Free Developer Plan)** using Docker.
- **Frontend (React):** Host on **Vercel** or **Netlify** (Free).
- **Database:** **Supabase (Free Tier)** (500MB storage, 10K monthly active users).
- **Queue/Cache:** **Upstash Redis (Free Tier)** or Render's free Redis add-on.

**Integrations:**
- **WhatsApp:** Meta Developer Account (Test mode / Sandbox uses free internal messaging).
- **SMS Sandbox:** Fast2SMS free test credits (~₹50 credit on signup).
- **Vision AI:** Groq (Llama-3-vision) free tier or generic OCR libraries.
- **Monitoring:** Sentry Developer (Free, 5K errors/month).

**Setup Steps (Tier 1):**
1. Push frontend to Vercel.
2. Link backend repo to Render. Set branch to `main`.
3. Provide `.env` variables in the Render dashboard for Supabase and Upstash.
4. Scale Celery worker to 0 if idle time is a concern, relying purely on FastAPI.

---

### Tier 2: Paid and Real Deployment (Startup scale)
*Focus: Handling 800+ concurrent doctors with high availability and durability.*

**Infrastructure:**
- **Cloud Provider:** **AWS (EC2 t3.medium or larger)** or **DigitalOcean Droplets**.
- **Backend:** Gunicorn with 4 Async Uvicorn workers (`WEB_CONCURRENCY=4`), Caddy reverse proxy with automatic HTTPS.
- **Database:** Supabase Pro plan ($25/mo) or AWS RDS PostgreSQL + **PgBouncer** connection pooling.
- **Queue/Cache:** Managed Redis or self-hosted Redis container with AOF persistence.

**Integrations:**
- **WhatsApp:** Verified Meta Business Cloud API (1,000 free service/utility conversations per month, then pay-per-use).
- **SMS:** Fast2SMS bulk credits (₹0.15 - ₹0.20 per SMS).
- **Vision/AI:** NVIDIA NIM APIs or OpenAI gpt-4o-mini API for scale extraction.
- **Monitoring:** Datadog or managed Grafana/Prometheus stack.
- **Payments:** Razorpay live integration for booking fee collection.

**Setup Steps (Tier 2):**
1. Provision EC2 instance mapping an Elastic IP and custom domain.
2. Install Docker and Docker Compose.
3. Caddy will automatically provision Let's Encrypt SSL certificates.
4. Clone repo, edit `docker-compose.prod.yml`, `docker-compose.caddy.yml`, `Caddyfile`, and `.env` with production keys.
5. Deploy using `docker-compose -f docker-compose.prod.yml -f docker-compose.caddy.yml up -d --build`.
6. Enable CI/CD via GitHub Actions for automated, zero-downtime rolling updates.

---

## Health Checks

| Endpoint | Purpose |
|----------|---------|
| `/health` | Liveness probe |
| `/health/ready` | Readiness probe (checks DB) |

---

## Monitoring

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f fastapi
docker-compose logs -f worker
```

### Metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3003 (admin/admin)

### Tracing
- Sentry dashboard for error tracking

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Database connection fails | Check DATABASE_URL, ensure postgres is running |
| Redis connection fails | Check REDIS_URL, ensure redis is running |
| WhatsApp not sending | Verify META_WHATSAPP_TOKEN, phone number verified |
| File upload fails | Check Supabase credentials, bucket permissions |
| Worker not picking tasks | Check Redis connection, worker logs |

### Debug Commands

```bash
# Check service status
docker-compose ps

# View worker queue
docker-compose exec redis redis-cli LLEN celery

# Check database migrations
docker-compose exec fastapi alembic current
```
