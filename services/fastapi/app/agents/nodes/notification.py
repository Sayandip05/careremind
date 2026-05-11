"""
Notification nodes — each step of the send-reminder pipeline.
Logic extracted from NotificationService.send_reminder().
"""

import logging
from datetime import datetime, timezone

from app.agents.message_agent import MessageAgent
from app.agents.state import NotificationState
from app.core.security import encryption_service
from app.core.integrations.whatsapp_service import whatsapp_service
from app.features.appointments.models import Appointment
from app.features.patients.models import Patient
from app.features.reminders.models import ChannelType, ReminderStatus
from app.features.auth.models import Tenant

logger = logging.getLogger("careremind.agents.nodes.notification")

_message_agent = MessageAgent()


async def load_context_node(state: NotificationState) -> dict:
    """Node: load appointment, patient, and tenant from DB."""
    reminder = state["reminder"]
    db = state["db"]

    appointment = await db.get(Appointment, reminder.appointment_id)
    if not appointment:
        reminder.status = ReminderStatus.FAILED
        reminder.error_log = "Appointment not found"
        await db.flush()
        return {
            "status": "error",
            "error": "Appointment not found",
            "success": False,
        }

    patient = await db.get(Patient, appointment.patient_id)
    tenant = await db.get(Tenant, reminder.tenant_id)

    if not patient or not tenant:
        reminder.status = ReminderStatus.FAILED
        reminder.error_log = "Missing patient or tenant data"
        await db.flush()
        return {
            "status": "error",
            "error": "Missing related data",
            "success": False,
        }

    return {
        "appointment": appointment,
        "patient": patient,
        "tenant": tenant,
        "status": "loaded",
    }


async def check_optout_node(state: NotificationState) -> dict:
    """Node: check if patient has opted out."""
    if state.get("status") == "error":
        return {}  # Skip — already failed

    patient = state["patient"]
    reminder = state["reminder"]
    db = state["db"]

    if patient.is_optout:
        reminder.status = ReminderStatus.OPTOUT
        await db.flush()
        logger.info("Patient opted out — skipping reminder %s", reminder.id)
        return {
            "status": "optout",
            "error": "Patient opted out",
            "success": False,
        }

    return {"status": "active"}


async def decrypt_phone_node(state: NotificationState) -> dict:
    """Node: decrypt the patient's phone number."""
    if state.get("status") in ("error", "optout"):
        return {}

    patient = state["patient"]
    reminder = state["reminder"]
    db = state["db"]

    phone = encryption_service.decrypt(patient.phone_encrypted)
    if not phone:
        reminder.status = ReminderStatus.FAILED
        reminder.error_log = "Could not decrypt phone number"
        await db.flush()
        return {
            "status": "error",
            "error": "Phone decryption failed",
            "success": False,
        }

    return {"phone": phone, "status": "decrypted"}


async def generate_message_node(state: NotificationState) -> dict:
    """Node: generate personalized reminder message via MessageAgent."""
    if state.get("status") in ("error", "optout"):
        return {}

    reminder = state["reminder"]
    message = await _message_agent.generate(
        patient=state["patient"],
        appointment=state["appointment"],
        tenant=state["tenant"],
        use_ai_polish=False,
    )

    reminder.message_text = message
    reminder.language_used = (
        state["patient"].language_preference
        or state["tenant"].language_preference
        or "english"
    )

    return {"message": message, "status": "message_ready"}


async def try_whatsapp_node(state: NotificationState) -> dict:
    """Node: send reminder via WhatsApp (sole delivery channel)."""
    if state.get("status") in ("error", "optout"):
        return {}

    reminder = state["reminder"]
    db = state["db"]

    if not whatsapp_service.is_configured:
        reminder.status = ReminderStatus.FAILED
        reminder.error_log = (
            "WhatsApp not configured — set META_WHATSAPP_TOKEN and META_PHONE_NUMBER_ID"
        )
        reminder.retry_count += 1
        await db.flush()
        logger.warning("WhatsApp not configured for reminder %s", reminder.id)
        return {
            "status": "failed",
            "error": "WhatsApp credentials not set",
            "success": False,
        }

    result = await whatsapp_service.send_message(state["phone"], state["message"])
    if result["success"]:
        reminder.status = ReminderStatus.SENT
        reminder.channel = ChannelType.WHATSAPP
        reminder.sent_at = datetime.now(timezone.utc)
        await db.flush()
        return {
            "status": "sent",
            "channel": "whatsapp",
            "success": True,
        }

    # WhatsApp failed — mark reminder as failed
    logger.warning("WhatsApp failed for reminder %s: %s", reminder.id, result["error"])
    reminder.status = ReminderStatus.FAILED
    reminder.error_log = f"WhatsApp failed: {result['error']}"
    reminder.retry_count += 1
    await db.flush()
    return {
        "status": "failed",
        "error": result["error"],
        "success": False,
    }
