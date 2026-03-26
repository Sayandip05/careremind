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
| nginx | 80, 443 | Reverse proxy |
| fastapi | 8000 | API server |
| worker | - | Celery background tasks |
| scheduler | - | APScheduler cron jobs |
| dashboard | 3000 | React doctor dashboard |
| landing | 3002 | React marketing site |
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis (queue + cache) |
| prometheus | 9090 | Metrics collection |
| grafana | 3003 | Metrics visualization |

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

# WhatsApp
META_WHATSAPP_TOKEN=your-whatsapp-token
META_PHONE_NUMBER_ID=your-phone-id

# SMS
FAST2SMS_API_KEY=your-fast2sms-key

# Vision
VISION_BACKEND=nvidia
NVIDIA_API_KEY=your-nvidia-key

# Monitoring
SENTRY_DSN=your-sentry-dsn

# App
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:3002
```

---

## Production Deployment

### Prerequisites
- Docker & Docker Compose
- Domain name (for SSL)
- Supabase project
- Meta Developer account (WhatsApp)
- Sentry account (monitoring)

### Steps

1. **Configure SSL/TLS**
   - Get SSL certificates (Let's Encrypt or purchased)
   - Place in `infrastructure/nginx/ssl/`

2. **Update Environment**
   ```bash
   ENVIRONMENT=production
   CORS_ORIGINS=https://yourdomain.com
   ```

3. **Build & Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

4. **Run Migrations**
   ```bash
   docker-compose exec fastapi alembic upgrade head
   ```

5. **Verify**
   - Health: `curl https://yourdomain.com/health`
   - API docs: `https://yourdomain.com/docs`

---

## CI/CD Pipeline

### GitHub Actions (Example)

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r services/fastapi/requirements.txt
      - run: pytest services/fastapi/tests/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - docker-compose build
      - docker-compose push
```

---

## Rollback Steps

### Quick Rollback (Docker)

```bash
# Rollback to previous version
docker-compose down
docker-compose up -d --build $(docker-compose images -q fastapi | head -1)
```

### Database Rollback

```bash
# Rollback last migration
docker-compose exec fastapi alembic downgrade -1
```

---

## Free Tier Limits

| Service | Free Tier | Notes |
|---------|-----------|-------|
| Supabase | 500MB storage, 10K monthly active users | Enough for ~50 doctors |
| Meta WhatsApp | 100K free messages/day | After verification |
| Fast2SMS | Pay-per-use | ~₹0.50/sms |
| Sentry | 5K errors/month | Sufficient for dev |
| Grafana | Local only | No cloud free tier |
| Railway/Render | Free tier available | Can host Docker |

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
