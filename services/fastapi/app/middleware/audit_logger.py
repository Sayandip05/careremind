import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

logger = logging.getLogger("careremind.audit")

class AuditLogger(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host if request.client else "127.0.0.1"
        
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = "{0:.2f}".format(process_time)
        
        logger.info(
            f"{request.method} {request.url.path} "
            f"- HTTP {response.status_code} "
            f"- {client_ip} "
            f"- {formatted_process_time}ms"
        )
        return response
