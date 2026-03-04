from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

tenant_context: ContextVar[str] = ContextVar("tenant_id", default="")


class TenantContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID", "default")
        tenant_context.set(tenant_id)
        response = await call_next(request)
        return response
