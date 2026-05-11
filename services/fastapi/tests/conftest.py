"""
Pytest configuration and fixtures.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator

# Disable rate limiting BEFORE importing the app, so SlowAPI uses memory backend
# and the per-IP counters don't bleed between tests.
os.environ.setdefault("TESTING", "true")

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.main import app

# Import all models so SQLAlchemy knows about them
from app.features.auth.models import Tenant
from app.features.patients.models import Patient
from app.features.appointments.models import Appointment
from app.features.reminders.models import Reminder
from app.features.upload.models import UploadLog
from app.features.billing.models import Payment
from app.features.audit.models import AuditLog
from app.features.clinics.models import ClinicLocation
from app.features.booking.models import Booking, DailySchedule

# Test database URL (use file-based SQLite for tests to avoid connection issues)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """Create a test database engine."""
    import os
    # Remove test database if it exists
    if os.path.exists("./test.db"):
        os.remove("./test.db")
    
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()
    
    # Clean up test database
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database session override.
    
    - follow_redirects=True so 307 trailing-slash redirects are transparent.
    - Unique X-Forwarded-For per fixture instance prevents cross-test rate-limit bleed.
    """
    import uuid as _uuid

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Each test gets a distinct fake IP so rate-limit counters don't accumulate
    unique_ip = f"10.{_uuid.uuid4().int % 255}.{_uuid.uuid4().int % 255}.1"
    headers = {"X-Forwarded-For": unique_ip}

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=True,
        headers=headers,
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_tenant_data():
    """Sample tenant data for testing."""
    return {
        "doctor_name": "Dr. Test Sharma",
        "clinic_name": "Test Clinic",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "specialty": "general",
        "language_preference": "english",
    }


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    return {
        "name": "Test Patient",
        "phone": "+919876543210",
        "preferred_channel": "whatsapp",
        "language_preference": "english",
    }


@pytest.fixture
async def auth_headers(client: AsyncClient, sample_tenant_data):
    """Create a test user and return authorization headers.

    Uses the same unique-IP client from the `client` fixture so the
    rate limiter counter is consistent across register + login calls
    within a single test.
    """
    # Register a test tenant
    register_response = await client.post("/api/v1/auth/register", json=sample_tenant_data)
    assert register_response.status_code == 201, (
        f"Registration failed in auth_headers fixture: {register_response.text}"
    )

    # Login to get token — same client = same fake IP = within rate limit window
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": sample_tenant_data["email"],
            "password": sample_tenant_data["password"],
        }
    )
    assert login_response.status_code == 200, (
        f"Login failed in auth_headers fixture (status {login_response.status_code}): {login_response.text}"
    )

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
