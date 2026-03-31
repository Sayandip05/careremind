import time
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.cache import cache

logger = logging.getLogger("careremind.ratelimit")

class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        target_path = request.url.path

        # Stricter limit for auth endpoints to prevent brute force
        if target_path.startswith("/api/v1/auth/login"):
            limit = 10
            window = 60 # 10 requests per minute
        else:
            limit = 200
            window = 60 # 200 requests per minute global

        # Create distinct buckets (auth vs global)
        bucket = "auth" if "auth" in target_path else "global"
        key = f"rate_limit:{client_ip}:{bucket}"
        
        try:
            current = await cache.incr(key)
            if current == 1:
                await cache.expire(key, window)
            
            if current > limit:
                logger.warning(f"Rate limit exceeded for IP {client_ip} on {target_path}")
                return JSONResponse(
                    status_code=429, 
                    content={"detail": "Too Many Requests. Please slow down."}
                )
        except Exception as e:
            # Revert to 'fail-open' so the app continues if Redis temporarily drops
            logger.error(f"Redis rate limiter failed, bypassing: {e}")
            pass
            
        return await call_next(request)
