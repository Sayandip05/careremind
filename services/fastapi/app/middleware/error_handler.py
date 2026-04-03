"""
Global error handler middleware — catches all unhandled exceptions
and returns consistent JSON error responses.
"""

import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.exceptions import AppException

logger = logging.getLogger("careremind.errors")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Catches all exceptions and returns standardized error responses.
    
    - AppException: Returns the specified status code and message
    - Other exceptions: Returns 500 with generic message (production) or details (dev)
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except AppException as exc:
            # Our custom exceptions - return as-is
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        except Exception as exc:
            # Unexpected exceptions - log and return safe response
            logger.error(
                "Unhandled exception in %s %s: %s",
                request.method,
                request.url.path,
                exc,
                exc_info=True,
            )
            
            if settings.is_production:
                # Production: don't expose internal details
                return JSONResponse(
                    status_code=500,
                    content={"detail": "An unexpected error occurred. Please try again later."},
                )
            else:
                # Development: include traceback for debugging
                return JSONResponse(
                    status_code=500,
                    content={
                        "detail": str(exc),
                        "traceback": traceback.format_exc(),
                    },
                )
