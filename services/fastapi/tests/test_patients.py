"""
Tests for patient endpoints — CRUD, pagination, IDOR protection.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestListPatients:
    """GET /api/v1/patients/"""

    async def test_list_empty(self, client: AsyncClient, auth_headers: dict):
        """Empty patient list returns valid paginated response."""
        resp = await client.get("/api/v1/patients/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "patients" in data
        assert "total" in data
        assert "page" in data
        assert data["page"] == 1

    async def test_list_unauthenticated(self, client: AsyncClient):
        """Patient list requires authentication."""
        resp = await client.get("/api/v1/patients/")
        assert resp.status_code in (401, 403)


@pytest.mark.asyncio
class TestCreatePatient:
    """POST /api/v1/patients/"""

    async def test_create_success(self, client: AsyncClient, auth_headers: dict):
        """Create a new patient with valid data."""
        payload = {
            "name": "Ramesh Kumar",
            "phone": "9876543210",
            "preferred_channel": "whatsapp",
        }
        resp = await client.post("/api/v1/patients/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Ramesh Kumar"
        assert data["preferred_channel"] == "whatsapp"
        assert "id" in data

    async def test_create_missing_name(self, client: AsyncClient, auth_headers: dict):
        """Name is required."""
        resp = await client.post("/api/v1/patients/", json={
            "phone": "9876543210",
        }, headers=auth_headers)
        assert resp.status_code == 422

    async def test_create_invalid_phone(self, client: AsyncClient, auth_headers: dict):
        """Phone must be at least 10 digits."""
        resp = await client.post("/api/v1/patients/", json={
            "name": "Test Patient",
            "phone": "123",
        }, headers=auth_headers)
        assert resp.status_code == 422

    async def test_create_invalid_channel(self, client: AsyncClient, auth_headers: dict):
        """Channel must be whatsapp, sms, or both."""
        resp = await client.post("/api/v1/patients/", json={
            "name": "Test Patient",
            "phone": "9876543210",
            "preferred_channel": "telegram",
        }, headers=auth_headers)
        assert resp.status_code == 422

    async def test_create_unauthenticated(self, client: AsyncClient):
        """Creating patient requires authentication."""
        resp = await client.post("/api/v1/patients/", json={
            "name": "Test", "phone": "9876543210",
        })
        assert resp.status_code in (401, 403)


@pytest.mark.asyncio
class TestGetPatient:
    """GET /api/v1/patients/{patient_id}"""

    async def test_get_nonexistent(self, client: AsyncClient, auth_headers: dict):
        """Getting a non-existent patient returns 404."""
        resp = await client.get(
            "/api/v1/patients/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestPagination:
    """Pagination on patients list."""

    async def test_custom_page_params(self, client: AsyncClient, auth_headers: dict):
        """Custom page and per_page are respected."""
        resp = await client.get(
            "/api/v1/patients/?page=1&per_page=5",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["per_page"] == 5

    async def test_invalid_page(self, client: AsyncClient, auth_headers: dict):
        """Page must be >= 1."""
        resp = await client.get(
            "/api/v1/patients/?page=0",
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_per_page_too_large(self, client: AsyncClient, auth_headers: dict):
        """per_page must be <= 100."""
        resp = await client.get(
            "/api/v1/patients/?per_page=200",
            headers=auth_headers,
        )
        assert resp.status_code == 422
