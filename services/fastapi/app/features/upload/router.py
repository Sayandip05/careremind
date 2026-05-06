"""
Upload routes — Excel and photo upload endpoints.

Photo pipeline (human-in-the-loop):
  POST /upload/photo           → VLM extracts rows, returns them for review (nothing saved yet)
  POST /upload/photo/confirm   → Doctor confirms/edits rows → dedup → save to DB

Excel pipeline (fully automatic):
  POST /upload/excel           → parse → dedup → save (no review needed for structured data)

Bug fixes applied:
  - Bug 3: errors are now surfaced to the frontend; "success" only shown when rows actually extracted
  - Bug 4: SHA-256 file hash idempotency — same photo cannot be double-processed within 24 h
"""

import hashlib
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.ocr_agent import OcrAgent
from app.agents.orchestrator import Orchestrator
from app.core.database import get_db
from app.core.security import get_current_tenant
from app.core.storage import storage
from app.features.auth.models import Tenant
from app.features.upload.models import UploadLog, UploadStatus
from app.features.upload.schemas import PhotoConfirmRequest, PhotoExtractResponse

logger = logging.getLogger("careremind.api.upload")

router = APIRouter()
orchestrator = Orchestrator()
_ocr_agent = OcrAgent()

# Max file sizes
MAX_EXCEL_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_PHOTO_SIZE = 20 * 1024 * 1024   # 20 MB

# Idempotency window: reject re-uploads of the same file within this period
_DEDUP_WINDOW_HOURS = 24


def _sha256(data: bytes) -> str:
    """Return hex SHA-256 digest of bytes — used as idempotency key."""
    return hashlib.sha256(data).hexdigest()


async def _find_duplicate_upload(
    db: AsyncSession,
    tenant_id: str,
    file_hash: str,
    file_type: str,
) -> UploadLog | None:
    """
    Return an existing UploadLog if the same file (by SHA-256) was already
    successfully processed or is pending review within the dedup window.
    Returns None if no duplicate found.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=_DEDUP_WINDOW_HOURS)
    result = await db.execute(
        select(UploadLog).where(
            UploadLog.tenant_id == tenant_id,
            UploadLog.file_hash == file_hash,
            UploadLog.file_type == file_type,
            UploadLog.status.in_([
                UploadStatus.COMPLETED,
                UploadStatus.PENDING_REVIEW,
                UploadStatus.PARTIAL,
            ]),
            UploadLog.created_at >= cutoff,
        )
    )
    return result.scalar_one_or_none()


# ── Excel Upload (automatic pipeline) ─────────────────────────────────────────

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
        raise HTTPException(status_code=400, detail="Only .xlsx and .xls files accepted")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_EXCEL_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB)")

    tenant_id = str(tenant.id)
    file_hash = _sha256(file_bytes)

    # Bug 4: Idempotency check — prevent double-processing same Excel
    existing = await _find_duplicate_upload(db, tenant_id, file_hash, "excel")
    if existing:
        logger.info(
            "Duplicate Excel upload detected for tenant %s (hash=%s, original=%s)",
            tenant_id, file_hash[:12], existing.id,
        )
        return {
            "upload_id": existing.id,
            "status": "already_processed",
            "filename": existing.filename,
            "total_rows": existing.total_rows,
            "new_patients": existing.total_rows - existing.duplicates_skipped - existing.failed_rows,
            "duplicates": existing.duplicates_skipped,
            "skipped": existing.failed_rows,
            "errors": [],
            "note": "This file was already uploaded and processed. No duplicate entries created.",
        }

    upload_id = str(uuid.uuid4())
    storage_url = await storage.save(file.filename, file_bytes, tenant_id)

    upload_log = UploadLog(
        id=upload_id,
        tenant_id=tenant_id,
        filename=file.filename,
        storage_url=storage_url,
        file_type="excel",
        file_hash=file_hash,
        status=UploadStatus.PROCESSING,
    )
    db.add(upload_log)
    await db.flush()

    try:
        result = await orchestrator.process("excel", file_bytes, tenant_id, db)

        # Bug 3: Distinguish partial success from full success
        if result["total_rows"] == 0 and result["errors"]:
            upload_log.status = UploadStatus.FAILED
        elif result["skipped"] > 0 and result["new_patients"] == 0:
            upload_log.status = UploadStatus.FAILED
        elif result["skipped"] > 0:
            upload_log.status = UploadStatus.PARTIAL
        else:
            upload_log.status = UploadStatus.COMPLETED

        upload_log.total_rows = result["total_rows"]
        upload_log.duplicates_skipped = result["duplicates"]
        upload_log.failed_rows = result["skipped"]
        await db.flush()

        return {
            "upload_id": upload_id,
            "status": upload_log.status.value,
            "filename": file.filename,
            "total_rows": result["total_rows"],
            "new_patients": result["new_patients"],
            "duplicates": result["duplicates"],
            "skipped": result["skipped"],
            "errors": result["errors"],
        }

    except Exception as e:
        logger.error("Excel upload pipeline failed: %s", e, exc_info=True)
        upload_log.status = UploadStatus.FAILED
        await db.flush()
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")


# ── Photo Upload — Step 1: Extract (Human-in-the-Loop) ────────────────────────

@router.post("/photo", response_model=PhotoExtractResponse)
async def upload_photo(
    file: UploadFile = File(...),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a photo of a patient register.

    Step 1 of 2 (Human-in-the-Loop):
    - VLM (NVIDIA llama-3.2-11b-vision-instruct) extracts rows from the image
    - Extracted rows are returned to the doctor for review
    - Nothing is saved to the database yet
    - Doctor must call POST /upload/photo/confirm to finalize

    Idempotency: same photo uploaded twice within 24h returns the cached
    extraction result instead of re-running the VLM.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files accepted")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_PHOTO_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 20 MB)")

    tenant_id = str(tenant.id)
    file_hash = _sha256(file_bytes)
    filename = file.filename or "photo.jpg"

    # Bug 4: Idempotency — same photo already extracted and pending review
    existing = await _find_duplicate_upload(db, tenant_id, file_hash, "photo")
    if existing and existing.status == UploadStatus.PENDING_REVIEW:
        logger.info(
            "Duplicate photo upload — returning cached extraction for tenant %s (upload=%s)",
            tenant_id, existing.id,
        )
        cached_rows = json.loads(existing.extracted_data or "[]")
        return PhotoExtractResponse(
            upload_id=existing.id,
            status="pending_review",
            filename=existing.filename,
            extracted_rows=cached_rows,
            total_extracted=len(cached_rows),
            errors=[],
            provider="cached",
        )
    if existing and existing.status == UploadStatus.COMPLETED:
        logger.info(
            "Duplicate photo upload — already completed for tenant %s (upload=%s)",
            tenant_id, existing.id,
        )
        return PhotoExtractResponse(
            upload_id=existing.id,
            status="already_processed",
            filename=existing.filename,
            extracted_rows=[],
            total_extracted=existing.total_rows,
            errors=[],
            provider="cached",
        )

    # Save to storage
    storage_url = await storage.save(filename, file_bytes, tenant_id)
    upload_id = str(uuid.uuid4())

    upload_log = UploadLog(
        id=upload_id,
        tenant_id=tenant_id,
        filename=filename,
        storage_url=storage_url,
        file_type="photo",
        file_hash=file_hash,
        status=UploadStatus.PROCESSING,
    )
    db.add(upload_log)
    await db.flush()

    # Run VLM extraction
    try:
        ocr_result = await _ocr_agent.extract(file_bytes)
    except Exception as e:
        logger.error("OCR extraction failed for upload %s: %s", upload_id, e, exc_info=True)
        upload_log.status = UploadStatus.FAILED
        await db.flush()
        raise HTTPException(status_code=500, detail=f"Image processing failed: {e}")

    extracted_rows = ocr_result.get("rows", [])
    errors = ocr_result.get("errors", [])
    provider = ocr_result.get("provider", "nvidia")

    # Bug 3: If VLM returned nothing, mark as failed and surface the error
    if not extracted_rows and errors:
        upload_log.status = UploadStatus.FAILED
        await db.flush()
        logger.warning(
            "VLM extraction returned 0 rows for upload %s. Errors: %s",
            upload_id, errors,
        )
        return PhotoExtractResponse(
            upload_id=upload_id,
            status="failed",
            filename=filename,
            extracted_rows=[],
            total_extracted=0,
            errors=errors,
            provider=provider,
        )

    # Serialize extracted rows as JSON — stored for the confirm step
    # Convert date objects to strings so they're JSON-serializable
    serializable_rows = []
    for row in extracted_rows:
        serializable_rows.append({
            "name": row.get("name", ""),
            "phone": row.get("phone", ""),
            "visit_date": row["visit_date"].isoformat() if row.get("visit_date") else None,
            "next_visit_date": row["next_visit_date"].isoformat() if row.get("next_visit_date") else None,
        })

    upload_log.status = UploadStatus.PENDING_REVIEW
    upload_log.extracted_data = json.dumps(serializable_rows)
    upload_log.total_rows = len(serializable_rows)
    await db.flush()

    logger.info(
        "Photo extracted %d rows for tenant %s (upload=%s, provider=%s)",
        len(serializable_rows), tenant_id, upload_id, provider,
    )

    return PhotoExtractResponse(
        upload_id=upload_id,
        status="pending_review",
        filename=filename,
        extracted_rows=serializable_rows,
        total_extracted=len(serializable_rows),
        errors=errors,
        provider=provider,
    )


# ── Photo Upload — Step 2: Confirm & Save ─────────────────────────────────────

@router.post("/photo/confirm")
async def confirm_photo_upload(
    body: PhotoConfirmRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Step 2 of 2 (Human-in-the-Loop):
    Doctor has reviewed extracted rows and clicks "Confirm & Save".
    Only the confirmed_rows list is saved — doctor can remove or edit rows before confirming.

    Pipeline: Dedup → Save patients + appointments → Schedule reminders
    """
    tenant_id = str(tenant.id)

    # Load the pending upload log
    upload_log = await db.get(UploadLog, body.upload_id)
    if not upload_log:
        raise HTTPException(status_code=404, detail="Upload not found")
    if upload_log.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if upload_log.status != UploadStatus.PENDING_REVIEW:
        raise HTTPException(
            status_code=409,
            detail=f"Upload is not pending review (current status: {upload_log.status.value})",
        )

    if not body.confirmed_rows:
        # Doctor confirmed with no rows — mark as completed with 0 rows
        upload_log.status = UploadStatus.COMPLETED
        upload_log.total_rows = 0
        await db.flush()
        return {
            "upload_id": body.upload_id,
            "status": "completed",
            "total_rows": 0,
            "new_patients": 0,
            "duplicates": 0,
            "skipped": 0,
            "errors": [],
        }

    # Convert confirmed rows back to the format the orchestrator expects
    rows_for_pipeline = [
        {
            "name": row.name,
            "phone": row.phone,
            "visit_date": row.visit_date,
            "next_visit_date": row.next_visit_date,
        }
        for row in body.confirmed_rows
    ]

    try:
        # Run dedup + save using the orchestrator's persistence path directly
        # We inject pre-extracted rows into the graph state, skipping the VLM step
        from app.agents.graphs.ingestion import ingestion_graph
        from app.core.langsmith import get_langsmith_metadata, get_langsmith_tags

        result = await ingestion_graph.ainvoke(
            {
                "file_type": "photo",          # routes to extract_ocr, but we override below
                "file_bytes": b"",             # not needed — extraction already done
                "tenant_id": tenant_id,
                "db": db,
                # Inject pre-reviewed rows directly, bypassing VLM extraction
                "extracted_rows": rows_for_pipeline,
                "extraction_errors": [],
                "extraction_skipped": 0,
                "total_rows": len(rows_for_pipeline),
                "source": "photo",
            },
            config={
                "metadata": get_langsmith_metadata(
                    tenant_id=tenant_id,
                    operation="ingestion_confirm",
                    file_type="photo",
                ),
                "tags": get_langsmith_tags("ingestion", "photo", "human_confirmed"),
            },
        )

        errors = list(result.get("extraction_errors", []))
        errors.extend(result.get("save_errors", []))

        saved = result.get("saved_count", 0)
        duplicates = len(result.get("duplicate_rows", []))
        skipped = result.get("extraction_skipped", 0)

        upload_log.status = UploadStatus.COMPLETED if saved > 0 else UploadStatus.PARTIAL
        upload_log.total_rows = len(rows_for_pipeline)
        upload_log.duplicates_skipped = duplicates
        upload_log.failed_rows = skipped
        upload_log.extracted_data = None  # Clear — no longer needed after save
        await db.flush()

        logger.info(
            "Photo confirm: saved=%d duplicates=%d skipped=%d upload=%s",
            saved, duplicates, skipped, body.upload_id,
        )

        return {
            "upload_id": body.upload_id,
            "status": upload_log.status.value,
            "total_rows": len(rows_for_pipeline),
            "new_patients": saved,
            "duplicates": duplicates,
            "skipped": skipped,
            "errors": errors,
        }

    except Exception as e:
        logger.error("Photo confirm failed for upload %s: %s", body.upload_id, e, exc_info=True)
        upload_log.status = UploadStatus.FAILED
        await db.flush()
        raise HTTPException(status_code=500, detail=f"Save failed: {e}")
