"""
Excel processing task — runs the Excel ingestion pipeline as a background job.
Called when uploads are processed asynchronously (large files).
"""

import asyncio
import logging

from celery import shared_task

logger = logging.getLogger("careremind.worker.excel")


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(bind=True, max_retries=1, default_retry_delay=30)
def process_excel_upload(self, upload_id: str, tenant_id: str):
    """
    Process an Excel upload in the background.
    Loads file from storage, runs Excel → Dedup → Save pipeline.
    """
    return _run_async(_process_excel(upload_id, tenant_id))


async def _process_excel(upload_id: str, tenant_id: str):
    """Load file from upload_log, run orchestrator pipeline."""
    from app.agents.orchestrator import Orchestrator
    from app.core.database import async_session
    from app.features.upload.models import UploadLog, UploadStatus

    async with async_session() as db:
        upload_log = await db.get(UploadLog, upload_id)
        if not upload_log:
            return {"success": False, "error": "Upload not found"}

        # Load file from storage URL
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(upload_log.storage_url)
            if response.status_code != 200:
                upload_log.status = UploadStatus.FAILED
                await db.commit()
                return {"success": False, "error": "Could not download file"}
            file_bytes = response.content

        # Run pipeline
        orchestrator = Orchestrator()
        try:
            result = await orchestrator.process("excel", file_bytes, tenant_id, db)

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
            logger.error("Excel processing failed for %s: %s", upload_id, e)
            upload_log.status = UploadStatus.FAILED
            await db.commit()
            return {"success": False, "error": str(e)}
