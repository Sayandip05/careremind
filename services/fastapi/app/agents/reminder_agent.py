"""
Reminder Agent — Thin wrapper around the LangGraph scheduling graph.
Creates Reminder records for appointments based on specialty timing rules.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graphs.scheduling import scheduling_graph
from app.features.appointments.models import Appointment
from app.features.auth.models import Tenant
from app.features.reminders.models import Reminder

logger = logging.getLogger("careremind.agents.reminder")


class ReminderAgent:
    """Creates Reminder records via the LangGraph scheduling graph."""

    async def schedule_reminders(
        self,
        appointment: Appointment,
        tenant: Tenant,
        db: AsyncSession,
    ) -> list[Reminder]:
        """
        Create Reminder records for an appointment via LangGraph.
        Returns list of created Reminder objects.
        """
        result = await scheduling_graph.ainvoke({
            "appointment": appointment,
            "tenant": tenant,
            "db": db,
        })

        return result.get("created_reminders", [])
