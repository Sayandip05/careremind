"""
Scheduling nodes — specialty resolution, timing computation, and reminder creation.
Logic extracted from ReminderAgent.schedule_reminders().
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import SchedulingState
from app.features.reminders.models import Reminder, ReminderStatus
from app.specialty import get_specialty

logger = logging.getLogger("careremind.agents.nodes.scheduling")


async def resolve_specialty_node(state: SchedulingState) -> dict:
    """Node: determine the specialty and get reminder timing rules."""
    appointment = state["appointment"]
    tenant = state["tenant"]

    visit_date = appointment.visit_date
    if not visit_date:
        logger.info("No visit_date for appointment %s — skipping", appointment.id)
        return {
            "timings": [],
            "specialty_name": "unknown",
        }

    specialty_name = getattr(appointment, "specialty_override", None) or tenant.specialty
    specialty = get_specialty(specialty_name)
    timings = specialty.get_reminder_timing()

    return {
        "specialty_name": specialty_name,
        "specialty": specialty,
        "timings": timings,
    }


async def create_reminders_node(state: SchedulingState) -> dict:
    """Node: create Reminder records for each timing, skipping duplicates and past dates."""
    timings = state.get("timings", [])
    if not timings:
        return {"created_reminders": [], "skipped_count": 0}

    appointment = state["appointment"]
    tenant = state["tenant"]
    db = state["db"]
    visit_date = appointment.visit_date

    created: list[Reminder] = []
    skipped = 0
    reminder_number = 0

    for timing in timings:
        reminder_number += 1
        scheduled_at = timing.get_scheduled_at(visit_date)

        # Skip if in the past
        if scheduled_at < datetime.now(timezone.utc):
            logger.info(
                "Skipping past reminder: %s for appointment %s",
                timing.label, appointment.id,
            )
            skipped += 1
            continue

        # Check for duplicate
        existing = await db.execute(
            select(Reminder).where(
                Reminder.appointment_id == appointment.id,
                Reminder.tenant_id == str(tenant.id),
                Reminder.scheduled_at == scheduled_at,
            )
        )
        if existing.scalar_one_or_none():
            logger.info("Reminder already exists for %s at %s", appointment.id, scheduled_at)
            skipped += 1
            continue

        reminder = Reminder(
            id=str(uuid.uuid4()),
            tenant_id=str(tenant.id),
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            reminder_number=reminder_number,
            channel="whatsapp",
            scheduled_at=scheduled_at,
            status=ReminderStatus.PENDING,
            retry_count=0,
        )
        db.add(reminder)
        created.append(reminder)

    await db.flush()

    specialty = state.get("specialty")
    logger.info(
        "Created %d reminders for appointment %s (%s — %s)",
        len(created), appointment.id,
        specialty.get_specialty_name() if specialty else "unknown",
        ", ".join(t.label for t in timings),
    )

    return {
        "created_reminders": created,
        "skipped_count": skipped,
    }
