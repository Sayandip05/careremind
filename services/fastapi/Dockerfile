# ─────────────────────────────────────────────────────────────────────────────
# CareRemind — Production Dockerfile
#
# Two-stage build:
#   Stage 1 (builder) — installs all Python deps into a virtualenv
#   Stage 2 (runtime) — copies only the venv + app code into a slim final image
#
# Result: ~380 MB image (vs ~700 MB single-stage) with no build tools in prod.
#
# Runs as non-root user `appuser` — follows least-privilege principle.
#
# CMD = Gunicorn + UvicornWorker  (production ASGI server)
# Override CMD in docker-compose for Celery worker:
#   command: celery -A app.worker.celery_app worker ...
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# System deps needed only for compiling C extensions (cryptography, psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy requirements first — Docker layer cache means this only re-runs when
# requirements.txt changes, not on every code change.
COPY requirements.txt .

# Install into an isolated virtualenv so Stage 2 can COPY it cleanly
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip==24.0 && \
    pip install --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Runtime system deps only (no build tools — smaller attack surface)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user — principle of least privilege
RUN groupadd --system appgroup && \
    useradd  --system --gid appgroup --no-create-home appuser

WORKDIR /app

# Copy the pre-built virtualenv from Stage 1
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
# .dockerignore excludes: venv/, __pycache__/, .env, tests/, *.pyc, .git/
COPY --chown=appuser:appgroup . .

# ── Runtime config ────────────────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    # Number of Gunicorn workers — override via Render env var
    # Formula: (2 × CPU cores) + 1  →  free tier has 1 vCPU → use 2
    WEB_CONCURRENCY=2

# Expose API port
EXPOSE 8000

# ── Health check ──────────────────────────────────────────────────────────────
# Docker / Render uses this to determine container readiness.
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root before starting the process
USER appuser

# ── Production command ────────────────────────────────────────────────────────
# Gunicorn manages Uvicorn async workers.
# --workers        controlled via WEB_CONCURRENCY env var (Render dashboard)
# --timeout        120s  — allows slow OCR / DB migrations to complete
# --graceful-timeout 30s — K8s/Render sends SIGTERM; workers finish in-flight reqs
# --keep-alive     5s   — reuse connections for better throughput
CMD ["sh", "-c", \
     "gunicorn app.main:app \
      --workers ${WEB_CONCURRENCY:-2} \
      --worker-class uvicorn.workers.UvicornWorker \
      --bind 0.0.0.0:8000 \
      --timeout 120 \
      --graceful-timeout 30 \
      --keep-alive 5 \
      --access-logfile - \
      --error-logfile -"]
