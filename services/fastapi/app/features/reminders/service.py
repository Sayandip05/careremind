"""
Notification Service — Thin wrapper around the LangGraph notification graph.
Sends reminders via WhatsApp (Meta Cloud API).
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graphs.notification import notification_graph
from app.core.langsmith import get_langsmith_metadata, get_langsmith_tags
from app.features.reminders.models import Reminder

logger = logging.getLogger("careremind.services.notification")


class NotificationService:
    """
    Sends a reminder to a patient via the LangGraph notification graph.
    Flow: load context → check opt-out → decrypt phone →
          generate message → send via WhatsApp.
    """

    async def send_reminder(self, reminder: Reminder, db: AsyncSession) -> dict:
        """
        Process a single pending reminder through the notification graph.
        Returns {"success": bool, "channel": str, "error": str}.
        """
        result = await notification_graph.ainvoke(
            {
                "reminder": reminder,
                "db": db,
            },
            config={
                "metadata": get_langsmith_metadata(
                    tenant_id=reminder.tenant_id,
                    reminder_id=reminder.id,
                    patient_id=reminder.patient_id,
                    operation="notification",
                ),
                "tags": get_langsmith_tags("notification", "reminder"),
            },
        )

        return {
            "success": result.get("success", False),
            "channel": result.get("channel"),
            "error": result.get("error"),
        }


notification_service = NotificationService()
