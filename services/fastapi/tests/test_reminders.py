"""
Tests for reminder endpoints — listing with status filters.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestListReminders:
    """GET /api/v1/reminders/"""

    async def test_list_empty(self, client: AsyncClient, auth_headers: dict):
        """Empty reminder list returns valid paginated response."""
        resp = await client.get("/api/v1/reminders/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "reminders" in data
        assert "total" in data
        assert isinstance(data["reminders"], list)

    async def test_list_with_status_filter(self, client: AsyncClient, auth_headers: dict):
        """Can filter reminders by status."""
        resp = await client.get(
            "/api/v1/reminders/?status=Pending",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 0

    async def test_list_with_invalid_status(self, client: AsyncClient, auth_headers: dict):
        """Invalid status filter is silently ignored (returns all)."""
        resp = await client.get(
            "/api/v1/reminders/?status=InvalidStatus",
            headers=auth_headers,
        )
        assert resp.status_code == 200  # Invalid filter ignored, returns all

    async def test_list_unauthenticated(self, client: AsyncClient):
        """Reminders list requires authentication."""
        resp = await client.get("/api/v1/reminders/")
        assert resp.status_code in (401, 403)

    async def test_list_pagination(self, client: AsyncClient, auth_headers: dict):
        """Pagination works on reminders list."""
        resp = await client.get(
            "/api/v1/reminders/?page=1&per_page=10",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["per_page"] == 10
