"""
Shared test fixtures for CareRemind API tests.
Uses SQLite in-memory database for fast, isolated testing.
"""

import asyncio
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.tenant import Tenant


# ── Test Database (SQLite async) ─────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False,
)


# ── Override DB dependency ───────────────────────────────────
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


# ── Session-scoped event loop ───────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Create/drop tables per test session ─────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ── Test DB session ─────────────────────────────────────────
@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


# ── HTTP Client ─────────────────────────────────────────────
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Test Tenant (Doctor) ────────────────────────────────────
@pytest_asyncio.fixture
async def test_tenant(db: AsyncSession) -> Tenant:
    """Create a test doctor account and return it."""
    tenant_id = str(uuid.uuid4())
    tenant = Tenant(
        id=tenant_id,
        doctor_name="Dr. Test",
        clinic_name="Test Clinic",
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=get_password_hash("TestPass123"),
        specialty="general",
        language_preference="english",
        plan="free",
        is_active=True,
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


# ── Auth Token for test tenant ──────────────────────────────
@pytest_asyncio.fixture
async def auth_headers(test_tenant: Tenant) -> dict:
    """Return Authorization headers with a valid JWT for the test tenant."""
    token = create_access_token(
        tenant_id=str(test_tenant.id),
        email=test_tenant.email,
    )
    return {"Authorization": f"Bearer {token}"}
