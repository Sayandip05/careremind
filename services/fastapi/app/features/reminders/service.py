"""
Notification Service — Thin wrapper around the LangGraph notification graph.
Routes messages to WhatsApp (primary) or SMS (fallback).
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graphs.notification import notification_graph
from app.features.reminders.models import Reminder

logger = logging.getLogger("careremind.services.notification")


class NotificationService:
    """
    Sends a reminder to a patient via the LangGraph notification graph.
    Flow: load context → check opt-out → decrypt phone →
          generate message → try WhatsApp → fallback SMS.
    """

    async def send_reminder(self, reminder: Reminder, db: AsyncSession) -> dict:
        """
        Process a single pending reminder through the notification graph.
        Returns {"success": bool, "channel": str, "error": str}.
        """
        result = await notification_graph.ainvoke({
            "reminder": reminder,
            "db": db,
        })

        return {
            "success": result.get("success", False),
            "channel": result.get("channel"),
            "error": result.get("error"),
        }


notification_service = NotificationService()
