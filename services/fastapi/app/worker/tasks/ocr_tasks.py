"""
OCR processing task — runs the photo OCR pipeline as a background job.
"""

import asyncio
import logging

from celery import shared_task

logger = logging.getLogger("careremind.worker.ocr")


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(bind=True, max_retries=1, default_retry_delay=30)
def process_photo_upload(self, upload_id: str, tenant_id: str):
    """
    Process a photo upload in the background.
    Loads image from storage, runs OCR → Dedup → Save pipeline.
    """
    return _run_async(_process_photo(upload_id, tenant_id))


async def _process_photo(upload_id: str, tenant_id: str):
    """Load image from upload_log, run OCR orchestrator pipeline."""
    import httpx

    from app.agents.orchestrator import Orchestrator
    from app.core.database import async_session
    from app.core.config import settings
    from app.features.upload.models import UploadLog, UploadStatus

    async with async_session() as db:
        upload_log = await db.get(UploadLog, upload_id)
        if not upload_log:
            return {"success": False, "error": "Upload not found"}

        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_DEFAULT) as client:
            response = await client.get(upload_log.storage_url)
            if response.status_code != 200:
                upload_log.status = UploadStatus.FAILED
                await db.commit()
                return {"success": False, "error": "Could not download image"}
            file_bytes = response.content

        orchestrator = Orchestrator()
        try:
            result = await orchestrator.process("photo", file_bytes, tenant_id, db)

            upload_log.status = UploadStatus.COMPLETED
            upload_log.total_rows = result["total_rows"]
            upload_log.duplicates_skipped = result["duplicates"]
            upload_log.failed_rows = result["skipped"]
            await db.commit()

            return {
                "success": True,
                "new_patients": result["new_patients"],
                "duplicates": result["duplicates"],
                "errors": result["errors"],
            }
        except Exception as e:
            logger.error("OCR processing failed for %s: %s", upload_id, e)
            upload_log.status = UploadStatus.FAILED
            await db.commit()
            return {"success": False, "error": str(e)}
