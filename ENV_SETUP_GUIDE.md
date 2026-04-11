# Environment Configuration Guide

## 📁 File Structure

```
careremind/
├── .env                          # ✅ Main config (used by Docker & Local)
├── .env.example                  # ✅ Template for .env
├── .env.local.example            # ✅ Template for local dev
├── docker-compose.yml            # Reads root .env
└── services/fastapi/
    ├── .env                      # ❌ DEPRECATED - Remove this
    └── app/core/config.py        # Reads root .env
```

---

## 🎯 Which `.env` File to Use?

### For Docker Deployment (Recommended)
**Use**: Root `.env` file

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env

# Run with Docker
docker-compose up
```

**Why?**
- ✅ Single source of truth
- ✅ Docker Compose automatically reads it
- ✅ All services use same config
- ✅ Easier to manage
- ✅ CI/CD friendly

### For Local Development (Without Docker)
**Use**: Root `.env` or `.env.local`

```bash
# Option 1: Use .env (same as Docker)
cp .env.example .env
# Edit DATABASE_URL to use localhost instead of 'postgres'
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/careremind

# Option 2: Use .env.local (separate from Docker)
cp .env.local.example .env.local
# Pydantic will read .env.local if it exists
```

**Why?**
- ✅ Can have different configs for Docker vs Local
- ✅ `.env.local` overrides `.env` if both exist
- ✅ Keeps Docker config separate

---

## 🔧 Configuration Differences

### Docker Configuration (`.env`)
```bash
# Use Docker service names
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/careremind
REDIS_URL=redis://redis:6379
```

### Local Configuration (`.env.local`)
```bash
# Use localhost
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/careremind
REDIS_URL=redis://localhost:6379
```

---

## 🚀 Quick Start

### 1. For Docker Deployment

```bash
# 1. Copy template
cp .env.example .env

# 2. Edit .env (optional - defaults work for Docker)
# DATABASE_URL is already set to use Docker service names

# 3. Start all services
docker-compose up -d

# 4. Run migrations
docker-compose exec fastapi alembic upgrade head

# 5. Seed database
docker-compose exec fastapi python -m scripts.seed_db
```

### 2. For Local Development

```bash
# 1. Copy template
cp .env.local.example .env.local

# 2. Edit .env.local with your local database
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/careremind

# 3. Install dependencies
cd services/fastapi
pip install -r requirements.txt

# 4. Run migrations
alembic upgrade head

# 5. Seed database
python -m scripts.seed_db

# 6. Start backend
uvicorn app.main:app --reload
```

---

## 📝 Required vs Optional Variables

### ✅ Required (Must Set)
```bash
DATABASE_URL=postgresql+asyncpg://...  # Database connection
JWT_SECRET_KEY=...                     # Min 32 chars
```

### ⚠️ Recommended (For Full Features)
```bash
REDIS_URL=redis://...                  # For caching & queue
SUPABASE_URL=...                       # For file storage
SUPABASE_KEY=...                       # For file storage
```

### 🔓 Optional (Can Leave Empty)
```bash
# All these are optional - system works without them
META_WHATSAPP_TOKEN=                   # WhatsApp API
META_PHONE_NUMBER_ID=                  # WhatsApp API
RAZORPAY_KEY_ID=                       # Payment gateway
RAZORPAY_SECRET=                       # Payment gateway
GROQ_API_KEY=                          # AI message generation
OPENAI_API_KEY=                        # AI OCR & messages
NVIDIA_API_KEY=                        # AI OCR
FAST2SMS_API_KEY=                      # SMS fallback
FIELD_ENCRYPTION_KEY=                  # PII encryption
SENTRY_DSN=                            # Error tracking
```

---

## 🐳 Docker Compose Behavior

### How It Works

```yaml
# docker-compose.yml
services:
  fastapi:
    env_file:
      - .env  # ← Reads root .env automatically
```

**What happens:**
1. Docker Compose reads root `.env`
2. Passes all variables to containers
3. FastAPI config.py reads from environment
4. All services share same config

### Environment Variable Priority

```
1. Shell environment variables (highest)
2. docker-compose.yml environment section
3. .env file (root level)
4. Default values in config.py (lowest)
```

---

## 🔒 Security Best Practices

### ✅ DO
- Keep `.env` in `.gitignore`
- Use `.env.example` as template (no secrets)
- Use strong JWT_SECRET_KEY (min 32 chars)
- Generate FIELD_ENCRYPTION_KEY properly
- Use environment variables in production

### ❌ DON'T
- Commit `.env` to Git
- Share `.env` file publicly
- Use default secrets in production
- Hardcode secrets in code

---

## 🧪 Testing Configuration

### For Tests
Tests use a separate in-memory database:

```python
# services/fastapi/tests/conftest.py
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

No `.env` needed for tests!

---

## 🚨 Troubleshooting

### "Config not loading"
**Problem**: FastAPI not reading `.env`  
**Solution**: Run from project root, not from `services/fastapi/`

```bash
# ❌ Wrong
cd services/fastapi
uvicorn app.main:app

# ✅ Correct
cd careremind  # project root
cd services/fastapi
uvicorn app.main:app
```

### "Database connection failed"
**Problem**: Wrong DATABASE_URL for environment  
**Solution**: Check if using correct service name

```bash
# For Docker
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/careremind

# For Local
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/careremind
```

### "Multiple .env files"
**Problem**: Have both root `.env` and `services/fastapi/.env`  
**Solution**: Delete `services/fastapi/.env`, use only root `.env`

```bash
rm services/fastapi/.env
```

---

## 📚 Summary

| Scenario | File to Use | Location |
|----------|-------------|----------|
| Docker Deployment | `.env` | Root |
| Local Development | `.env` or `.env.local` | Root |
| CI/CD Pipeline | Environment Variables | - |
| Testing | Not needed | - |
| Template | `.env.example` | Root |

**Best Practice**: Use root `.env` for everything. It's simpler and Docker-ready! 🎯
