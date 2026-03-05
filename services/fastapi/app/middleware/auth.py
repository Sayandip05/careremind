"""
Auth middleware — request-level logging and JWT header validation.

NOTE: Actual tenant authentication is handled per-route via the
`get_current_tenant` dependency in `app.core.security`.
This middleware only handles request-level concerns like logging.
"""

import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("careremind.auth")

# Routes that do not require authentication
PUBLIC_PATHS = {
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/webhooks/whatsapp",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Lightweight middleware for:
    - Request timing / logging
    - Skipping auth on public paths (actual auth is per-route via Depends)
    """

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.debug(
            "%s %s — %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response
