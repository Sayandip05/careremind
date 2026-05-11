"""
Request timeout middleware — prevents long-running requests from blocking workers.

Applies different timeouts based on endpoint type:
- Upload endpoints: 120 seconds (large files)
- Health checks: 5 seconds (fast response)
- Normal API: 60 seconds (default)
"""

import asyncio
import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger("careremind.timeout")


class TimeoutMiddleware(BaseHTTPMiddleware):
    """
    Global request timeout middleware.

    Prevents long-running requests from blocking Gunicorn workers.
    Returns 504 Gateway Timeout if request exceeds time limit.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Determine timeout based on endpoint type
        if path.startswith("/api/v1/upload"):
            timeout = settings.REQUEST_TIMEOUT_UPLOAD  # 120s for file uploads
        elif path.startswith("/health"):
            timeout = settings.REQUEST_TIMEOUT_HEALTH  # 5s for health checks
        else:
            timeout = settings.REQUEST_TIMEOUT_DEFAULT  # 60s for normal API

        try:
            # Wrap request in timeout
            return await asyncio.wait_for(call_next(request), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(
                "Request timeout: %s %s (%.1fs exceeded)", request.method, path, timeout
            )
            return JSONResponse(
                status_code=504,
                content={
                    "detail": f"Request timeout after {timeout}s. The operation took too long to complete."
                },
            )
