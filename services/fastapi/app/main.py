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
from app.core.config import settings
from app.core.database import get_db
from app.middleware.auth import AuthMiddleware
from app.middleware.tenant_context import TenantContextMiddleware

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
    logger.info("CareRemind API starting up — environment: %s", settings.ENVIRONMENT)
    yield
    logger.info("CareRemind API shutting down")


# ── App Instance ─────────────────────────────────────────────
app = FastAPI(
    title="CareRemind API",
    description="AI-powered patient appointment reminder system for Indian clinics",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# ── CORS Middleware ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Tenant Context Middleware ────────────────────────────────
app.add_middleware(TenantContextMiddleware)

# ── Auth Middleware ───────────────────────────────────────────
app.add_middleware(AuthMiddleware)

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
