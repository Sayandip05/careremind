"""
Upload routes — Excel and photo upload endpoints.
Triggers the full ingestion pipeline: extract → dedup → save.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import Orchestrator
from app.core.database import get_db
from app.core.security import get_current_tenant
from app.core.storage import storage
from app.features.auth.models import Tenant
from app.features.upload.models import UploadLog, UploadStatus

logger = logging.getLogger("careremind.api.upload")

router = APIRouter()
orchestrator = Orchestrator()

# Max file sizes
MAX_EXCEL_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_PHOTO_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/excel")
async def upload_excel(
    file: UploadFile = File(...),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload an Excel file (.xlsx/.xls) containing patient data.
    Pipeline: ExcelAgent → Dedup → Save patients + appointments.
    """
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Only .xlsx and .xls files accepted"
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_EXCEL_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB)")

    tenant_id = str(tenant.id)
    upload_id = str(uuid.uuid4())

    # Save file to storage
    storage_url = await storage.save(file.filename, file_bytes, tenant_id)

    # Create upload log
    upload_log = UploadLog(
        id=upload_id,
        tenant_id=tenant_id,
        filename=file.filename,
        storage_url=storage_url,
        file_type="excel",
        status=UploadStatus.PROCESSING,
    )
    db.add(upload_log)
    await db.flush()

    # Run pipeline
    try:
        result = await orchestrator.process("excel", file_bytes, tenant_id, db)

        upload_log.status = UploadStatus.COMPLETED.value
        upload_log.total_rows = result["total_rows"]
        upload_log.duplicates_skipped = result["duplicates"]
        upload_log.failed_rows = result["skipped"]

        await db.flush()

        return {
            "upload_id": upload_id,
            "status": "completed",
            "filename": file.filename,
            "total_rows": result["total_rows"],
            "new_patients": result["new_patients"],
            "duplicates": result["duplicates"],
            "skipped": result["skipped"],
            "errors": result["errors"],
        }

    except Exception as e:
        logger.error("Upload pipeline failed: %s", e, exc_info=True)
        upload_log.status = UploadStatus.FAILED
        await db.flush()
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")


@router.post("/photo")
async def upload_photo(
    file: UploadFile = File(...),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a photo of a patient register.
    Pipeline: OcrAgent (GPT-4o Mini vision) → Dedup → Save patients + appointments.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files accepted")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_PHOTO_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 20 MB)")

    tenant_id = str(tenant.id)
    upload_id = str(uuid.uuid4())

    # Save to storage
    storage_url = await storage.save(
        file.filename or "photo.jpg", file_bytes, tenant_id
    )

    # Create upload log
    upload_log = UploadLog(
        id=upload_id,
        tenant_id=tenant_id,
        filename=file.filename or "photo.jpg",
        storage_url=storage_url,
        file_type="photo",
        status=UploadStatus.PROCESSING,
    )
    db.add(upload_log)
    await db.flush()

    # Run pipeline
    try:
        result = await orchestrator.process("photo", file_bytes, tenant_id, db)

        upload_log.status = UploadStatus.COMPLETED
        upload_log.total_rows = result["total_rows"]
        upload_log.duplicates_skipped = result["duplicates"]
        upload_log.failed_rows = result["skipped"]

        await db.flush()

        return {
            "upload_id": upload_id,
            "status": "completed",
            "filename": file.filename,
            "total_rows": result["total_rows"],
            "new_patients": result["new_patients"],
            "duplicates": result["duplicates"],
            "skipped": result["skipped"],
            "errors": result["errors"],
        }

    except Exception as e:
        logger.error("Photo upload pipeline failed: %s", e, exc_info=True)
        upload_log.status = UploadStatus.FAILED
        await db.flush()
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
