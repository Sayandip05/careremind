"""
Persistence node — saves new patients + appointments to DB.
Logic extracted from the old Orchestrator.process() method.
"""

import logging
import uuid
from datetime import date

from app.agents.state import IngestionState
from app.features.appointments.models import Appointment, UploadSource
from app.features.patients.models import Patient, PreferredChannel

logger = logging.getLogger("careremind.agents.nodes.persistence")


async def save_to_db_node(state: IngestionState) -> dict:
    """Node: create Patient + Appointment records for each new (non-duplicate) row."""
    new_rows = state.get("new_rows", [])
    db = state["db"]
    tenant_id = state["tenant_id"]
    source_str = state.get("source", "excel")

    source = UploadSource.EXCEL if source_str == "excel" else UploadSource.PHOTO

    saved_count = 0
    errors: list[str] = []

    for row in new_rows:
        try:
            patient = Patient(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                name=row["name"],
                phone_encrypted=row["_phone_encrypted"],
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

    await db.flush()

    logger.info(
        "Persistence node: saved %d patients, %d errors",
        saved_count, len(errors),
    )

    return {
        "saved_count": saved_count,
        "save_errors": errors,
    }
