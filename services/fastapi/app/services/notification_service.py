"""
Notification Service — Routes messages to WhatsApp (primary) or SMS (fallback).
Also generates the message content via MessageAgent.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.message_agent import MessageAgent
from app.core.security import encryption_service
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.reminder import ChannelType, Reminder, ReminderStatus
from app.models.tenant import Tenant
from app.services.sms_service import sms_service
from app.services.whatsapp_service import whatsapp_service

logger = logging.getLogger("careremind.services.notification")

message_agent = MessageAgent()


class NotificationService:
    """
    Sends a reminder to a patient.
    Flow: generate message → try WhatsApp → fallback to SMS → update status.
    """

    async def send_reminder(self, reminder: Reminder, db: AsyncSession) -> dict:
        """
        Process a single pending reminder:
        1. Load related patient, appointment, tenant
        2. Check opt-out
        3. Generate personalized message
        4. Send via WhatsApp (primary) → SMS (fallback)
        5. Update reminder status
        """
        # Load related data
        appointment = await db.get(Appointment, reminder.appointment_id)
        if not appointment:
            reminder.status = ReminderStatus.FAILED
            reminder.error_log = "Appointment not found"
            await db.flush()
            return {"success": False, "error": "Appointment not found"}

        patient = await db.get(Patient, appointment.patient_id)
        tenant = await db.get(Tenant, reminder.tenant_id)

        if not patient or not appointment or not tenant:
            reminder.status = ReminderStatus.FAILED
            reminder.error_log = "Missing patient, appointment, or tenant data"
            await db.flush()
            return {"success": False, "error": "Missing related data"}

        # Check opt-out
        if patient.is_optout:
            reminder.status = ReminderStatus.OPTOUT
            await db.flush()
            logger.info("Patient opted out — skipping reminder %s", reminder.id)
            return {"success": False, "error": "Patient opted out"}

        # Decrypt phone
        phone = encryption_service.decrypt(patient.phone_encrypted)
        if not phone:
            reminder.status = ReminderStatus.FAILED
            reminder.error_log = "Could not decrypt phone number"
            await db.flush()
            return {"success": False, "error": "Phone decryption failed"}

        # Generate message
        message = await message_agent.generate(
            patient=patient,
            appointment=appointment,
            tenant=tenant,
            use_ai_polish=False,  # Use templates for speed; AI polish in Phase 5 scheduler
        )

        reminder.message_text = message
        reminder.language_used = patient.language_preference or tenant.language_preference or "english"

        # Try WhatsApp first
        if whatsapp_service.is_configured:
            result = await whatsapp_service.send_message(phone, message)
            if result["success"]:
                reminder.status = ReminderStatus.SENT
                reminder.channel = ChannelType.WHATSAPP
                reminder.sent_at = datetime.now(timezone.utc)
                await db.flush()
                return {"success": True, "channel": "whatsapp"}

            logger.warning("WhatsApp failed for reminder %s: %s", reminder.id, result["error"])

        # Fallback to SMS
        if sms_service.is_configured:
            result = await sms_service.send_message(phone, message)
            if result["success"]:
                reminder.status = ReminderStatus.SENT
                reminder.channel = ChannelType.SMS
                reminder.sent_at = datetime.now(timezone.utc)
                await db.flush()
                return {"success": True, "channel": "sms"}

            logger.warning("SMS failed for reminder %s: %s", reminder.id, result["error"])

        # Both channels failed
        reminder.status = ReminderStatus.FAILED
        reminder.error_log = "Both WhatsApp and SMS failed"
        await db.flush()
        return {"success": False, "error": "All channels failed"}


notification_service = NotificationService()
