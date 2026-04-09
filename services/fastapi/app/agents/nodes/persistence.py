"""
Persistence node — saves new patients + appointments to DB.
Logic extracted from the old Orchestrator.process() method.
"""

import logging
import uuid
from datetime import date

from sqlalchemy import select

from app.agents.state import IngestionState
from app.agents.graphs.scheduling import scheduling_graph
from app.core.security import encryption_service
from app.features.appointments.models import Appointment, UploadSource
from app.features.auth.models import Tenant
from app.features.patients.models import Patient, PreferredChannel

logger = logging.getLogger("careremind.agents.nodes.persistence")


async def save_to_db_node(state: IngestionState) -> dict:
    """Node: create Patient + Appointment records for each new (non-duplicate) row.
    
    Also schedules reminders for each created appointment via the scheduling graph.
    """
    new_rows = state.get("new_rows", [])
    db = state["db"]
    tenant_id = state["tenant_id"]
    source_str = state.get("source", "excel")

    source = UploadSource.EXCEL if source_str == "excel" else UploadSource.PHOTO

    saved_count = 0
    reminders_created = 0
    errors: list[str] = []

    # Load tenant for scheduling
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        errors.append(f"Tenant {tenant_id} not found")
        return {"saved_count": 0, "save_errors": errors, "reminders_created": 0}

    for row in new_rows:
        try:
            # Use hash from dedup node if available, otherwise compute it
            phone_hash = row.get("_phone_hash")
            if not phone_hash:
                phone_hash = encryption_service.hash_phone(row["phone"])
            
            patient = Patient(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                name=row["name"],
                phone_encrypted=row["_phone_encrypted"],
                phone_hash=phone_hash,
                preferred_channel=PreferredChannel.WHATSAPP,
                language_preference="english",
            )
            db.add(patient)

            # Create appointment if visit dates are available
            appointment = None
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

            # Schedule reminders for this appointment
            if appointment:
                await db.flush()  # Ensure appointment has an ID
                try:
                    sched_result = await scheduling_graph.ainvoke({
                        "appointment": appointment,
                        "tenant": tenant,
                        "db": db,
                    })
                    created = sched_result.get("created_reminders", [])
                    reminders_created += len(created)
                except Exception as sched_e:
                    logger.error(
                        "Failed to schedule reminders for appointment %s: %s",
                        appointment.id, sched_e, exc_info=True
                    )
                    errors.append(f"Reminder scheduling failed for {row.get('name')}: {sched_e}")

        except Exception as e:
            errors.append(f"Failed to save patient '{row.get('name')}': {e}")
            logger.error("Save error: %s", e, exc_info=True)

    await db.flush()

    logger.info(
        "Persistence node: saved %d patients, %d reminders created, %d errors",
        saved_count, reminders_created, len(errors),
    )

    return {
        "saved_count": saved_count,
        "save_errors": errors,
        "reminders_created": reminders_created,
    }
