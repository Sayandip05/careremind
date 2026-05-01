# Deployment Guide - CareRemind

**Version**: 1.0  
**Last Updated**: 2026-05-01

---

## Service Deployment Map

| Service | Platform | URL/Instance | Status |
|---------|----------|--------------|--------|
| **Frontend** | Vercel | `https://careremind.vercel.app` | Auto-deploy from `main` |
| **Backend API** | Render | `https://careremind-api.onrender.com` | Auto-deploy from `main` |
| **Database** | Supabase | Project: `careremind-prod` | Managed PostgreSQL |
| **Redis** | Upstash | Instance: `careremind-cache` | Serverless Redis |
| **Storage** | Supabase | Bucket: `uploads` | File storage |

---

## Environment Variables

### Required (Production)
```
DATABASE_URL
SUPABASE_URL
SUPABASE_KEY
REDIS_URL
JWT_SECRET_KEY
FIELD_ENCRYPTION_KEY
API_BASE_URL
FRONTEND_URL
CORS_ORIGINS
```

### Optional (Feature-Dependent)
```
# AI & OCR
OPENAI_API_KEY
NVIDIA_API_KEY
GROQ_API_KEY

# Messaging
META_WHATSAPP_TOKEN
META_PHONE_NUMBER_ID
FAST2SMS_API_KEY

# Payments
RAZORPAY_KEY_ID
RAZORPAY_SECRET
RAZORPAY_WEBHOOK_SECRET

# OAuth
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
FACEBOOK_CLIENT_ID
FACEBOOK_CLIENT_SECRET

# Monitoring
LANGSMITH_API_KEY
SENTRY_DSN
```

### Configuration
```
ENVIRONMENT
JWT_ALGORITHM
JWT_EXPIRY_HOURS
SCHEDULER_TIMEZONE
DB_POOL_SIZE
DB_MAX_OVERFLOW
HTTP_TIMEOUT_DEFAULT
HTTP_MAX_CONNECTIONS
```

**Note**: See `.env.example` for complete list with descriptions.

---

## Deployment Steps

### 1. Initial Setup

**Database (Supabase)**:
```bash
1. Create project at https://supabase.com
2. Copy DATABASE_URL from Settings → Database
3. Run migrations:
   cd services/fastapi
   alembic upgrade head
```

**Redis (Upstash)**:
```bash
1. Create database at https://upstash.com
2. Copy REDIS_URL from dashboard
```

### 2. Backend Deployment (Render)

**One-Time Setup**:
```bash
1. Connect GitHub repo to Render
2. Create Web Service:
   - Build Command: pip install -r services/fastapi/requirements.txt
   - Start Command: cd services/fastapi && gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   - Root Directory: /
3. Add environment variables from Render dashboard
4. Deploy
```

**Auto-Deploy**:
- Push to `main` branch → Render auto-deploys
- Build time: ~3-5 minutes
- Zero-downtime deployment

### 3. Frontend Deployment (Vercel)

**One-Time Setup**:
```bash
1. Connect GitHub repo to Vercel
2. Configure:
   - Framework: Vite
   - Root Directory: frontend
   - Build Command: npm run build
   - Output Directory: dist
3. Add environment variables:
   - VITE_API_BASE_URL=https://careremind-api.onrender.com
4. Deploy
```

**Auto-Deploy**:
- Push to `main` branch → Vercel auto-deploys
- Build time: ~1-2 minutes
- Preview deployments for PRs

### 4. Background Workers (Optional)

**Render Background Worker**:
```bash
1. Create Background Worker service
2. Start Command: cd services/fastapi && celery -A app.worker.celery_app worker --loglevel=info
3. Use same environment variables as API
4. Deploy
```

---

## CI/CD Pipeline

### Trigger Events
- **Push to `main`**: Auto-deploy to production
- **Pull Request**: Create preview deployment (Vercel only)
- **Manual**: Trigger from platform dashboard

### Pipeline Flow
```
1. GitHub Push
   ↓
2. Render/Vercel Webhook Triggered
   ↓
3. Clone Repository
   ↓
4. Install Dependencies
   ↓
5. Run Build (if applicable)
   ↓
6. Health Check
   ↓
7. Deploy (Zero-Downtime)
   ↓
8. Notify (Slack/Email)
```

### Build Checks
- **Backend**: Python syntax, dependency resolution
- **Frontend**: TypeScript compilation, Vite build
- **Health**: `/health` endpoint returns 200

---

## Health Checks

### Backend API
```bash
# Health endpoint
GET https://careremind-api.onrender.com/health

Response:
{
  "status": "healthy",
  "timestamp": "2026-05-01T10:30:00Z",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

### Frontend
```bash
# Root endpoint
GET https://careremind.vercel.app

Response: 200 OK (HTML)
```

### Database
```bash
# From backend container
psql $DATABASE_URL -c "SELECT 1;"
```

---

## Local Development

### Quick Start
```bash
# 1. Clone repository
git clone https://github.com/yourusername/careremind.git
cd careremind

# 2. Copy environment file
cp .env.example .env
# Edit .env with your credentials

# 3. Start services (Docker)
docker-compose up

# 4. Run migrations
docker-compose exec api alembic upgrade head

# 5. Access services
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Without Docker
```bash
# Backend
cd services/fastapi
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

---

## Common Deployment Issues

### 1. Database Connection Failed
**Symptom**: `connection refused` or `timeout`

**Fix**:
```bash
# Check DATABASE_URL format
postgresql+asyncpg://postgres:PASSWORD@HOST:5432/postgres

# Verify Supabase IP allowlist (should be 0.0.0.0/0 for Render)
# Check Supabase → Settings → Database → Connection Pooling
```

### 2. Redis Connection Failed
**Symptom**: `ECONNREFUSED` or `timeout`

**Fix**:
```bash
# Check REDIS_URL format
redis://default:PASSWORD@HOST:PORT

# Verify Upstash allows connections from Render IPs
# Use TLS if required: rediss://...
```

### 3. CORS Errors
**Symptom**: `blocked by CORS policy`

**Fix**:
```bash
# Update CORS_ORIGINS in backend .env
CORS_ORIGINS=https://careremind.vercel.app,https://careremind-preview.vercel.app

# Restart backend service
```

### 4. Build Failures
**Symptom**: Deployment fails during build

**Fix**:
```bash
# Backend: Check requirements.txt syntax
pip install -r services/fastapi/requirements.txt

# Frontend: Check package.json
cd frontend && npm install

# Clear build cache on platform dashboard
```

### 5. Migration Errors
**Symptom**: `alembic.util.exc.CommandError`

**Fix**:
```bash
# Check current migration version
alembic current

# Rollback if needed
alembic downgrade -1

# Re-run migrations
alembic upgrade head

# If stuck, reset (CAUTION: data loss)
alembic stamp head
```

### 6. Environment Variables Not Loading
**Symptom**: `KeyError` or `None` values

**Fix**:
```bash
# Verify variables are set in platform dashboard
# Check for typos in variable names
# Restart service after adding variables
# Use quotes for values with special characters
```

### 7. Slow Cold Starts (Render Free Tier)
**Symptom**: First request takes 30+ seconds

**Fix**:
```bash
# Upgrade to paid tier for always-on instances
# Or use cron job to ping health endpoint every 10 minutes
# https://cron-job.org/en/ → GET /health every 10 min
```

### 8. File Upload Fails
**Symptom**: `413 Payload Too Large` or `timeout`

**Fix**:
```bash
# Check Supabase storage bucket permissions
# Verify SUPABASE_KEY is service role key (not anon key)
# Check file size limits in code (10MB Excel, 20MB Photo)
```

---

## Monitoring

### Logs
```bash
# Render: Dashboard → Logs tab (real-time)
# Vercel: Dashboard → Deployments → View Logs

# Local Docker:
docker-compose logs -f api
docker-compose logs -f worker
```

### Metrics
```bash
# Render: Dashboard → Metrics (CPU, Memory, Response Time)
# Vercel: Dashboard → Analytics (Page Views, Performance)
# Supabase: Dashboard → Database → Performance
# Upstash: Dashboard → Metrics (Commands, Latency)
```

### Alerts
```bash
# Render: Settings → Notifications → Slack/Email
# Vercel: Settings → Notifications → Slack/Email
# Supabase: Settings → Alerts → Email
```

---

## Rollback

### Backend (Render)
```bash
1. Dashboard → Deployments
2. Find previous successful deployment
3. Click "Redeploy"
4. Confirm
```

### Frontend (Vercel)
```bash
1. Dashboard → Deployments
2. Find previous deployment
3. Click "..." → Promote to Production
4. Confirm
```

### Database (Supabase)
```bash
# Use Alembic to rollback migrations
alembic downgrade -1

# Or restore from backup
# Supabase → Database → Backups → Restore
```

---

## Production Checklist

- [ ] All required environment variables set
- [ ] Database migrations applied
- [ ] FIELD_ENCRYPTION_KEY generated and set
- [ ] JWT_SECRET_KEY changed from default
- [ ] CORS_ORIGINS includes production URLs
- [ ] Health checks passing
- [ ] SSL/HTTPS enabled (automatic on Vercel/Render)
- [ ] Monitoring alerts configured
- [ ] Backup strategy in place (Supabase auto-backups)
- [ ] API rate limiting configured
- [ ] Error tracking enabled (Sentry)

---

## Support

**Documentation**: `docs/` folder  
**Issues**: GitHub Issues  
**Health Check**: `GET /health`

---

**Document Version**: 1.0  
**Last Updated**: 2026-05-01
