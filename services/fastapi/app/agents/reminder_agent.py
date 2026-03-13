"""
Reminder Agent — Creates Reminder records for appointments
based on the doctor's specialty timing rules.

Timing model: reminders fire AFTER the visit date (7 days, 30 days).
"""

import logging
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment
from app.models.reminder import Reminder, ReminderStatus
from app.models.tenant import Tenant
from app.specialty import get_specialty

logger = logging.getLogger("careremind.agents.reminder")


class ReminderAgent:
    """Creates Reminder records based on specialty-specific timing."""

    async def schedule_reminders(
        self,
        appointment: Appointment,
        tenant: Tenant,
        db: AsyncSession,
    ) -> list[Reminder]:
        """
        Create Reminder records for an appointment.

        Timing: 1st reminder 7 days after visit, 2nd 30 days after visit.
        Uses visit_date (the date patient came in).
        """
        visit_date = appointment.visit_date
        if not visit_date:
            logger.info("No visit_date for appointment %s — skipping", appointment.id)
            return []

        # Determine specialty
        specialty_name = getattr(appointment, "specialty_override", None) or tenant.specialty
        specialty = get_specialty(specialty_name)

        timings = specialty.get_reminder_timing()
        created: list[Reminder] = []
        reminder_number = 0

        for timing in timings:
            reminder_number += 1
            scheduled_at = timing.get_scheduled_at(visit_date)

            # Skip if scheduled_at is in the past
            if scheduled_at < datetime.now():
                logger.info(
                    "Skipping past reminder: %s for appointment %s",
                    timing.label, appointment.id,
                )
                continue

            # Check for duplicate (same appointment + same scheduled_at)
            existing = await db.execute(
                select(Reminder).where(
                    Reminder.appointment_id == appointment.id,
                    Reminder.tenant_id == str(tenant.id),
                    Reminder.scheduled_at == scheduled_at,
                )
            )
            if existing.scalar_one_or_none():
                logger.info("Reminder already exists for %s at %s", appointment.id, scheduled_at)
                continue

            reminder = Reminder(
                id=str(uuid.uuid4()),
                tenant_id=str(tenant.id),
                appointment_id=appointment.id,
                reminder_number=reminder_number,
                channel="whatsapp",
                scheduled_at=scheduled_at,
                status=ReminderStatus.PENDING,
            )
            db.add(reminder)
            created.append(reminder)

        await db.flush()

        logger.info(
            "Created %d reminders for appointment %s (%s — %s)",
            len(created), appointment.id, specialty.get_specialty_name(),
            ", ".join(t.label for t in timings),
        )

        return created
