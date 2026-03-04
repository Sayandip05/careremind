from fastapi import FastAPI
from app.api.v1 import router
from app.middleware.auth import AuthMiddleware
from app.core.config import settings

app = FastAPI(
    title="CareRemind API",
    description="AI-powered healthcare reminder system",
    version="1.0.0",
)

app.add_middleware(AuthMiddleware)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
