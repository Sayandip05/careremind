import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.features.auth.router import router as auth_router
from app.features.patients.router import router as patients_router
from app.features.appointments.router import router as appointments_router
from app.features.reminders.router import router as reminders_router
from app.features.upload.router import router as upload_router
from app.features.billing.router import router as billing_router
from app.features.staff.router import router as staff_router
from app.features.audit.router import router as audit_router
from app.features.dashboard.router import router as dashboard_router
from app.features.webhooks.router import router as webhooks_router
from app.features.clinics.router import router as clinics_router
from app.features.booking.router import router as booking_router
from app.core.config import settings
from app.core.database import get_db
from app.middleware.auth import AuthMiddleware
from app.middleware.tenant_context import TenantContextMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.audit_logger import AuditLogger
from app.middleware.input_sanitizer import SecurityHeadersMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware

# ── Sentry Initialization ────────────────────────────────────
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1 if settings.is_production else 1.0,
        send_default_pii=False,
    )

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if settings.is_production else logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("careremind")


# ── Lifespan (startup/shutdown) ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on application startup and shutdown."""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from app.scheduler.jobs import SCHEDULED_JOBS
    
    logger.info("CareRemind API starting up — environment: %s", settings.ENVIRONMENT)
    
    # Start scheduler for background jobs
    scheduler = AsyncIOScheduler()
    
    for job_config in SCHEDULED_JOBS:
        func = job_config["func"]
        trigger_type = job_config["trigger"]
        job_id = job_config["id"]
        job_name = job_config["name"]
        
        if trigger_type == "cron":
            trigger = CronTrigger(
                hour=job_config.get("hour"),
                minute=job_config.get("minute"),
            )
        elif trigger_type == "interval":
            trigger = IntervalTrigger(
                minutes=job_config.get("minutes"),
            )
        else:
            logger.error("Unknown trigger type: %s", trigger_type)
            continue
        
        scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            name=job_name,
            replace_existing=job_config.get("replace_existing", True),
        )
        
        logger.info("Scheduled job: %s", job_name)
    
    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(SCHEDULED_JOBS))
    
    yield
    
    logger.info("CareRemind API shutting down")
    scheduler.shutdown()
    logger.info("Scheduler stopped")


# ── App Instance ─────────────────────────────────────────────
app = FastAPI(
    title="CareRemind API",
    description="AI-powered patient appointment reminder system for Indian clinics",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# ── Middlewares ──────────────────────────────────────────────
# Applied in reverse order of evaluation

app.add_middleware(ErrorHandlerMiddleware)  # Catch all unhandled exceptions
app.add_middleware(AuthMiddleware)
app.add_middleware(TenantContextMiddleware)
app.add_middleware(RateLimiterMiddleware)  # 3. Rate Limit IPs
app.add_middleware(SecurityHeadersMiddleware) # 2. Append Security Headers
app.add_middleware(AuditLogger) # 1. Log HTTP requests

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Router ───────────────────────────────────────────────
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(patients_router, prefix="/api/v1/patients", tags=["patients"])
app.include_router(
    appointments_router, prefix="/api/v1/appointments", tags=["appointments"]
)
app.include_router(reminders_router, prefix="/api/v1/reminders", tags=["reminders"])
app.include_router(upload_router, prefix="/api/v1/upload", tags=["upload"])
app.include_router(billing_router, prefix="/api/v1/billing", tags=["billing"])
app.include_router(staff_router, prefix="/api/v1/staff", tags=["staff"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(webhooks_router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(clinics_router, prefix="/api/v1/clinics", tags=["clinics"])
app.include_router(booking_router, prefix="/api/v1/booking", tags=["booking"])


# ── Health Check ─────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint for load balancers and monitoring."""
    return {"status": "healthy", "service": "careremind-api"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check - verifies database connectivity.
    """
    try:
        await db.execute(select(1))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error("Database health check failed: %s", e)
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "database": "disconnected"},
        )


# ── Global Exception Handler ─────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all for unhandled exceptions.
    In production, log the error but don't expose internals.
    """
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again later."
            if settings.is_production
            else str(exc)
        },
    )
