"""
Storage Service — Uploads files to Supabase Storage.
Falls back to local filesystem if Supabase is not configured.
"""

import logging
import uuid
from pathlib import Path

import httpx

from app.core.config import settings

logger = logging.getLogger("careremind.core.storage")


class StorageService:
    """Handles file uploads to Supabase Storage or local filesystem."""

    BUCKET = "uploads"

    async def save(self, filename: str, data: bytes, tenant_id: str) -> str:
        """
        Save a file and return its storage URL.
        Files are organized as: uploads/{tenant_id}/{uuid}_{filename}
        """
        # Generate unique filename to prevent collisions
        unique_name = f"{tenant_id}/{uuid.uuid4().hex}_{filename}"

        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            return await self._save_supabase(unique_name, data)
        else:
            return self._save_local(unique_name, data)

    async def _save_supabase(self, path: str, data: bytes) -> str:
        """Upload to Supabase Storage bucket."""
        url = f"{settings.SUPABASE_URL}/storage/v1/object/{self.BUCKET}/{path}"
        headers = {
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            "Content-Type": "application/octet-stream",
            "x-upsert": "true",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, content=data, headers=headers)

            if response.status_code not in (200, 201):
                logger.error(
                    "Supabase Storage upload failed %d: %s",
                    response.status_code,
                    response.text,
                )
                # Fall back to local
                return self._save_local(path, data)

        public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.BUCKET}/{path}"
        logger.info("File uploaded to Supabase: %s", public_url)
        return public_url

    def _save_local(self, path: str, data: bytes) -> str:
        """Fallback: save to local uploads/ directory."""
        upload_dir = Path("uploads") / Path(path).parent
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = Path("uploads") / path
        file_path.write_bytes(data)

        logger.info("File saved locally: %s", file_path)
        return str(file_path)


storage = StorageService()
