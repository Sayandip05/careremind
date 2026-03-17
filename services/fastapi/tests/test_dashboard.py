"""
Tests for dashboard stats endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestDashboardStats:
    """GET /api/v1/dashboard/stats"""

    async def test_stats_authenticated(self, client: AsyncClient, auth_headers: dict):
        """Authenticated doctor gets dashboard stats."""
        resp = await client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_patients" in data
        assert "pending_reminders" in data
        assert "sent_reminders" in data
        assert "failed_reminders" in data
        assert "success_rate" in data
        assert "total_uploads" in data
        # All counts should be >= 0
        assert data["total_patients"] >= 0
        assert data["success_rate"] >= 0

    async def test_stats_unauthenticated(self, client: AsyncClient):
        """Dashboard stats require authentication."""
        resp = await client.get("/api/v1/dashboard/stats")
        assert resp.status_code in (401, 403)
