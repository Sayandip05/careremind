"""
Tests for authentication endpoints — register, login, profile.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    """POST /api/v1/auth/register"""

    async def test_register_success(self, client: AsyncClient):
        """New doctor can register with valid data."""
        payload = {
            "doctor_name": "Dr. Sharma",
            "clinic_name": "Sharma Clinic",
            "email": "sharma@example.com",
            "password": "SecurePass123",
            "specialty": "dermatology",
            "language_preference": "hindi",
        }
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["doctor_name"] == "Dr. Sharma"
        assert data["clinic_name"] == "Sharma Clinic"
        assert data["email"] == "sharma@example.com"
        assert data["is_active"] is True

    async def test_register_duplicate_email(self, client: AsyncClient):
        """Cannot register with an email that already exists."""
        payload = {
            "doctor_name": "Dr. Duplicate",
            "clinic_name": "Dup Clinic",
            "email": "duplicate@example.com",
            "password": "SecurePass123",
        }
        # First registration
        resp1 = await client.post("/api/v1/auth/register", json=payload)
        assert resp1.status_code == 200

        # Second registration with same email
        resp2 = await client.post("/api/v1/auth/register", json=payload)
        assert resp2.status_code in (400, 409)

    async def test_register_short_password(self, client: AsyncClient):
        """Password must be at least 8 characters."""
        payload = {
            "doctor_name": "Dr. Short",
            "clinic_name": "Short Clinic",
            "email": "short@example.com",
            "password": "123",
        }
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 422  # Pydantic validation error

    async def test_register_missing_fields(self, client: AsyncClient):
        """Required fields must be present."""
        resp = await client.post("/api/v1/auth/register", json={})
        assert resp.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        """Email must be valid format."""
        payload = {
            "doctor_name": "Dr. Bad",
            "clinic_name": "Bad Clinic",
            "email": "not-an-email",
            "password": "SecurePass123",
        }
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    """POST /api/v1/auth/login"""

    async def test_login_success(self, client: AsyncClient):
        """Registered doctor can login and get JWT."""
        # Register first
        reg_payload = {
            "doctor_name": "Dr. Login",
            "clinic_name": "Login Clinic",
            "email": "login@example.com",
            "password": "SecurePass123",
        }
        await client.post("/api/v1/auth/register", json=reg_payload)

        # Login
        resp = await client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "SecurePass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["doctor_name"] == "Dr. Login"

    async def test_login_wrong_password(self, client: AsyncClient):
        """Login fails with wrong password."""
        resp = await client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "WrongPassword",
        })
        assert resp.status_code in (400, 401)

    async def test_login_nonexistent_email(self, client: AsyncClient):
        """Login fails for non-registered email."""
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "SecurePass123",
        })
        assert resp.status_code in (400, 401, 404)


@pytest.mark.asyncio
class TestProfile:
    """GET /api/v1/auth/me"""

    async def test_get_profile_authenticated(self, client: AsyncClient, auth_headers: dict):
        """Authenticated doctor can get their profile."""
        resp = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["doctor_name"] == "Dr. Test"
        assert data["clinic_name"] == "Test Clinic"

    async def test_get_profile_no_token(self, client: AsyncClient):
        """Unauthenticated request is rejected."""
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code in (401, 403)

    async def test_get_profile_invalid_token(self, client: AsyncClient):
        """Invalid JWT is rejected."""
        resp = await client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid.token.here",
        })
        assert resp.status_code == 401
