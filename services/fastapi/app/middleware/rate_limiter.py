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
        
        # Extract user ID from JWT token (if authenticated)
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                import jwt
                from app.core.config import settings
                token = auth_header.split(" ")[1]
                payload = jwt.decode(
                    token, 
                    settings.JWT_SECRET_KEY, 
                    algorithms=[settings.JWT_ALGORITHM]
                )
                user_id = payload.get("tenant_id")
            except Exception:
                pass  # Invalid token, fall back to IP-based limiting

        # Stricter limit for auth endpoints to prevent brute force
        if target_path.startswith("/api/v1/auth/login"):
            limit = 10
            window = 60  # 10 requests per minute
            bucket = "auth"
        else:
            limit = 200 if not user_id else 1000  # Higher limit for authenticated users
            window = 60  # per minute
            bucket = "global"

        # Rate limit by user ID (if authenticated) or IP (if not)
        if user_id:
            key = f"rate_limit:user:{user_id}:{bucket}"
        else:
            key = f"rate_limit:ip:{client_ip}:{bucket}"
        
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
