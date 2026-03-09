"""
Orchestrator — The main ingestion pipeline.
Routes file type → correct agent → normalize → dedup → save to DB.
"""

import logging
import uuid
from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.dedup_agent import DedupAgent
from app.agents.excel_agent import ExcelAgent
from app.agents.ocr_agent import OcrAgent
from app.models.appointment import Appointment, UploadSource
from app.models.patient import Patient, PreferredChannel

logger = logging.getLogger("careremind.agents.orchestrator")

ExtractedRow = dict[str, Any]


class Orchestrator:
    """
    Main pipeline controller.
    Takes a file, routes to the correct agent, deduplicates,
    and saves new patients + appointments to the database.
    """

    def __init__(self):
        self.excel_agent = ExcelAgent()
        self.ocr_agent = OcrAgent()
        self.dedup_agent = DedupAgent()

    async def process(
        self,
        file_type: str,          # "excel" or "photo"
        file_bytes: bytes,
        tenant_id: str,
        db: AsyncSession,
    ) -> dict:
        """
        Full pipeline: extract → dedup → save.

        Returns:
            {
                "total_rows": int,
                "new_patients": int,
                "duplicates": int,
                "skipped": int,
                "errors": [str, ...],
            }
        """
        errors: list[str] = []

        # ── Step 1: Extract rows using the correct agent ─────
        if file_type == "excel":
            result = await self.excel_agent.extract(file_bytes)
            source = UploadSource.EXCEL
        elif file_type == "photo":
            result = await self.ocr_agent.extract(file_bytes)
            source = UploadSource.PHOTO
        else:
            return {
                "total_rows": 0,
                "new_patients": 0,
                "duplicates": 0,
                "skipped": 0,
                "errors": [f"Unknown file type: {file_type}"],
            }

        rows = result["rows"]
        errors.extend(result.get("errors", []))
        skipped = result.get("skipped", 0)

        if not rows:
            return {
                "total_rows": result.get("total_rows", 0),
                "new_patients": 0,
                "duplicates": 0,
                "skipped": skipped,
                "errors": errors,
            }

        # ── Step 2: Deduplicate ──────────────────────────────
        dedup_result = await self.dedup_agent.deduplicate(rows, tenant_id, db)
        new_rows = dedup_result["new"]
        dup_rows = dedup_result["duplicates"]

        # ── Step 3: Save new patients + appointments ─────────
        saved_count = 0
        for row in new_rows:
            try:
                patient = Patient(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    name=row["name"],
                    phone_encrypted=row["_phone_encrypted"],  # Already encrypted by dedup agent
                    preferred_channel=PreferredChannel.WHATSAPP,
                    language_preference="english",
                )
                db.add(patient)

                # Create appointment if visit dates are available
                if row.get("visit_date") or row.get("next_visit_date"):
                    appointment = Appointment(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant_id,
                        patient_id=patient.id,
                        visit_date=row.get("visit_date") or date.today(),
                        next_visit_date=row.get("next_visit_date"),
                        source=source,
                    )
                    db.add(appointment)

                saved_count += 1
            except Exception as e:
                errors.append(f"Failed to save patient '{row.get('name')}': {e}")
                logger.error("Save error: %s", e, exc_info=True)

        # Flush all saves
        await db.flush()

        logger.info(
            "Pipeline complete: %d total, %d new, %d duplicates, %d skipped",
            result.get("total_rows", 0), saved_count, len(dup_rows), skipped,
        )

        return {
            "total_rows": result.get("total_rows", 0),
            "new_patients": saved_count,
            "duplicates": len(dup_rows),
            "skipped": skipped,
            "errors": errors,
        }
