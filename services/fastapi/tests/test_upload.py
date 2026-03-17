"""
Tests for upload endpoints — Excel and photo uploads.
External APIs (OCR, storage) are mocked.
"""

import io
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUploadExcel:
    """POST /api/v1/upload/excel"""

    async def test_reject_non_excel(self, client: AsyncClient, auth_headers: dict):
        """Only .xlsx/.xls files are accepted."""
        fake_file = io.BytesIO(b"not an excel file")
        resp = await client.post(
            "/api/v1/upload/excel",
            files={"file": ("test.txt", fake_file, "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "xlsx" in resp.json()["detail"].lower() or "xls" in resp.json()["detail"].lower()

    async def test_reject_oversized_file(self, client: AsyncClient, auth_headers: dict):
        """Files over 10 MB are rejected."""
        # Create an 11 MB fake file
        large_file = io.BytesIO(b"x" * (11 * 1024 * 1024))
        resp = await client.post(
            "/api/v1/upload/excel",
            files={"file": ("big.xlsx", large_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "large" in resp.json()["detail"].lower()

    async def test_upload_unauthenticated(self, client: AsyncClient):
        """Upload requires authentication."""
        fake_file = io.BytesIO(b"data")
        resp = await client.post(
            "/api/v1/upload/excel",
            files={"file": ("test.xlsx", fake_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        assert resp.status_code in (401, 403)


@pytest.mark.asyncio
class TestUploadPhoto:
    """POST /api/v1/upload/photo"""

    async def test_reject_non_image(self, client: AsyncClient, auth_headers: dict):
        """Only image files are accepted."""
        fake_file = io.BytesIO(b"not an image")
        resp = await client.post(
            "/api/v1/upload/photo",
            files={"file": ("test.txt", fake_file, "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "image" in resp.json()["detail"].lower()

    async def test_reject_oversized_photo(self, client: AsyncClient, auth_headers: dict):
        """Photos over 20 MB are rejected."""
        large_file = io.BytesIO(b"x" * (21 * 1024 * 1024))
        resp = await client.post(
            "/api/v1/upload/photo",
            files={"file": ("big.jpg", large_file, "image/jpeg")},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "large" in resp.json()["detail"].lower()

    async def test_upload_photo_unauthenticated(self, client: AsyncClient):
        """Photo upload requires authentication."""
        fake_file = io.BytesIO(b"data")
        resp = await client.post(
            "/api/v1/upload/photo",
            files={"file": ("test.jpg", fake_file, "image/jpeg")},
        )
        assert resp.status_code in (401, 403)
