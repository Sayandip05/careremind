"""
Reminder Agent — Creates Reminder records for appointments
based on the doctor's specialty timing rules.
"""

import logging
import uuid
from datetime import date, timedelta

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

        Uses the tenant's specialty (or appointment's specialty_override)
        to determine timing. Each timing offset creates one Reminder.
        """
        visit_date = appointment.next_visit_date
        if not visit_date:
            logger.info("No next_visit_date for appointment %s — skipping", appointment.id)
            return []

        # Determine specialty
        specialty_name = appointment.specialty_override or tenant.specialty
        specialty = get_specialty(specialty_name)

        timings = specialty.get_reminder_timing()
        created: list[Reminder] = []

        for timing in timings:
            scheduled_at = timing.get_scheduled_at(visit_date)

            # Skip if scheduled_at is in the past
            from datetime import datetime
            if scheduled_at < datetime.now():
                logger.info(
                    "Skipping past reminder: %s for appointment %s",
                    timing.label, appointment.id,
                )
                continue

            # Check for duplicate (same appointment + same timing label)
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
                channel="whatsapp",
                scheduled_at=scheduled_at,
                status=ReminderStatus.PENDING,
            )
            db.add(reminder)
            created.append(reminder)

        await db.flush()

        logger.info(
            "Created %d reminders for appointment %s (%s specialty)",
            len(created), appointment.id, specialty.get_specialty_name(),
        )

        return created
