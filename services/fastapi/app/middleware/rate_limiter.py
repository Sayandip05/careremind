from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from collections import defaultdict
import time


class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        return await call_next(request)
