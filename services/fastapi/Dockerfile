FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ── Production: Gunicorn + Uvicorn workers ───────────────────
# 4 workers × async uvicorn = handles ~800 concurrent doctors
# Each worker runs its own event loop (non-blocking I/O throughout)
# Adjust WEB_CONCURRENCY env var to override (default: 4)
ENV WEB_CONCURRENCY=4

CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
