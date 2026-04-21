"""
Auth middleware — request-level logging and JWT header validation.

NOTE: Actual tenant authentication is handled per-route via the
`get_current_tenant` dependency in `app.core.security`.
This middleware only handles request-level concerns like logging.
"""

import logging
import time
from typing import Callable

from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("careremind.auth")

PUBLIC_PATHS = {
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/specialties",
    "/api/v1/auth/login/google",
    "/api/v1/auth/login/facebook",
    "/api/v1/auth/callback/google",
    "/api/v1/auth/callback/facebook",
    "/api/v1/webhooks/whatsapp",
    "/api/v1/webhooks/razorpay",
    "/api/v1/contact",
}

PUBLIC_PATH_PREFIXES = {
    "/docs",
    "/redoc",
    "/openapi.json",
}


def is_public_path(path: str) -> bool:
    """Check if the path is public (no auth required)."""
    if path in PUBLIC_PATHS:
        return True
    for prefix in PUBLIC_PATH_PREFIXES:
        if path.startswith(prefix):
            return True
    return False


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Lightweight middleware for:
    - Request timing / logging
    - Skip metrics for public paths
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        is_public = is_public_path(path)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        if not is_public:
            logger.debug(
                "%s %s — %d (%.1fms)",
                request.method,
                path,
                response.status_code,
                duration_ms,
            )

        return response
