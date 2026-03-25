"""
Webhook routes — WhatsApp incoming messages and payment callbacks.
Handles opt-out (STOP) messages AND incoming files (images, documents) from doctors.
"""

import base64
import logging
import uuid
from typing import Optional

import httpx

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import Orchestrator
from app.core.database import get_db
from app.core.security import encryption_service
from app.core.storage import storage
from app.features.patients.models import Patient
from app.features.reminders.models import Reminder, ReminderStatus

logger = logging.getLogger("careremind.api.webhooks")

router = APIRouter()

OPTOUT_KEYWORDS = {"stop", "unsubscribe", "cancel", "quit", "end", "band", "bnd"}

orchestrator = Orchestrator()


@router.get("/whatsapp")
async def whatsapp_verify(
    request: Request,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    WhatsApp webhook verification (required by Meta).
    Meta sends a GET with hub.challenge — we echo it back.
    """
    if hub_mode == "subscribe" and hub_challenge:
        return PlainTextResponse(content=hub_challenge)
    return JSONResponse(status_code=403, content={"error": "Verification failed"})


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Receives incoming WhatsApp messages.

    Handles:
    - Text: opt-out keywords (STOP, unsubscribe, etc.)
    - Image: process like /upload/photo (OCR)
    - Document: process like /upload/excel
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=200, content={"status": "ok"})

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            for message in value.get("messages", []):
                await _handle_whatsapp_message(message, db, value)

    return JSONResponse(status_code=200, content={"status": "ok"})


async def _handle_whatsapp_message(message: dict, db: AsyncSession, value: dict):
    """Process incoming WhatsApp message - text, image, or document."""
    message_type = message.get("type", "text")
    sender = message.get("from", "")

    logger.info("Received WhatsApp message type: %s from %s", message_type, sender[-4:])

    metadata = value.get("metadata", {})
    phone_number_id = metadata.get("phone_number_id", "")

    if message_type == "text":
        text = (message.get("text", {}).get("body", "")).strip().lower()
        if text in OPTOUT_KEYWORDS:
            await _handle_optout(sender, db)
            logger.info("Opt-out processed for ...%s", sender[-4:])
        else:
            await _handle_unknown_text(sender, text, phone_number_id)

    elif message_type == "image":
        await _handle_whatsapp_image(message, sender, db, phone_number_id)

    elif message_type == "document":
        await _handle_whatsapp_document(message, sender, db, phone_number_id)

    else:
        logger.warning("Unhandled message type: %s", message_type)


async def _handle_unknown_text(sender: str, text: str, phone_number_id: str):
    """Send a help message for unknown text commands."""
    help_message = (
        "Welcome to CareRemind Bot!\n\n"
        "You can send:\n"
        "• Images of patient registers (we'll extract data)\n"
        "• Excel files with patient list\n"
        "• Send STOP to unsubscribe\n\n"
        "To upload patients, please use the Dashboard web interface."
    )
    await _send_whatsapp_message(sender, help_message, phone_number_id)


async def _handle_whatsapp_image(
    message: dict, sender: str, db: AsyncSession, phone_number_id: str
):
    """Handle incoming image - download, process with OCR."""
    try:
        media_id = message.get("image", {}).get("id")
        if not media_id:
            await _send_whatsapp_message(
                sender, "Could not process image. Please try again.", phone_number_id
            )
            return

        file_bytes = await _download_media(media_id)
        tenant_id = await _find_tenant_by_whatsapp(sender, db)

        if not tenant_id:
            await _send_whatsapp_message(
                sender,
                "Your WhatsApp number is not registered. Please login to your dashboard first.",
                phone_number_id,
            )
            return

        result = await orchestrator.process("photo", file_bytes, tenant_id, db)
        await db.commit()

        response = (
            f"✅ Image processed!\n\n"
            f"Total rows: {result['total_rows']}\n"
            f"New patients: {result['new_patients']}\n"
            f"Duplicates skipped: {result['duplicates']}\n"
            f"Errors: {len(result['errors'])}"
        )
        await _send_whatsapp_message(sender, response, phone_number_id)

    except Exception as e:
        logger.error("Failed to process WhatsApp image: %s", e)
        await _send_whatsapp_message(
            sender, f"Error processing image: {str(e)[:50]}", phone_number_id
        )


async def _handle_whatsapp_document(
    message: dict, sender: str, db: AsyncSession, phone_number_id: str
):
    """Handle incoming document - download, process with Excel parser."""
    try:
        doc = message.get("document", {})
        media_id = doc.get("id")
        filename = doc.get("filename", "document.xlsx")

        if not media_id:
            await _send_whatsapp_message(
                sender, "Could not process document. Please try again.", phone_number_id
            )
            return

        if not filename.lower().endswith((".xlsx", ".xls")):
            await _send_whatsapp_message(
                sender,
                "Only Excel files (.xlsx, .xls) are supported. Please upload via dashboard for other formats.",
                phone_number_id,
            )
            return

        file_bytes = await _download_media(media_id)
        tenant_id = await _find_tenant_by_whatsapp(sender, db)

        if not tenant_id:
            await _send_whatsapp_message(
                sender,
                "Your WhatsApp number is not registered. Please login to your dashboard first.",
                phone_number_id,
            )
            return

        result = await orchestrator.process("excel", file_bytes, tenant_id, db)
        await db.commit()

        response = (
            f"✅ Excel processed!\n\n"
            f"Total rows: {result['total_rows']}\n"
            f"New patients: {result['new_patients']}\n"
            f"Duplicates skipped: {result['duplicates']}\n"
            f"Errors: {len(result['errors'])}"
        )
        await _send_whatsapp_message(sender, response, phone_number_id)

    except Exception as e:
        logger.error("Failed to process WhatsApp document: %s", e)
        await _send_whatsapp_message(
            sender, f"Error processing Excel: {str(e)[:50]}", phone_number_id
        )


async def _download_media(media_id: str) -> bytes:
    """Download media from Meta WhatsApp API."""
    from app.core.config import settings

    url = f"https://graph.facebook.com/v21.0/{media_id}"
    headers = {"Authorization": f"Bearer {settings.META_WHATSAPP_TOKEN}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        data = response.json()

        download_url = data.get("url")
        if not download_url:
            raise ValueError("No download URL in media response")

        download_response = await client.get(download_url, headers=headers)
        return download_response.content


async def _find_tenant_by_whatsapp(phone: str, db: AsyncSession) -> str | None:
    """Find tenant by their registered WhatsApp number."""
    from app.features.auth.models import Tenant
    from app.utils.phone_formatter import normalize_phone

    phone = normalize_phone(phone)
    if not phone:
        return None

    result = await db.execute(select(Tenant).where(Tenant.whatsapp_number == phone))
    tenant = result.scalar_one_or_none()
    return str(tenant.id) if tenant else None


async def _send_whatsapp_message(to: str, message: str, phone_number_id: str):
    """Send a WhatsApp text message back to user."""
    from app.core.config import settings
    import httpx

    url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.META_WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }

    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, headers=headers)
    except Exception as e:
        logger.error("Failed to send WhatsApp message: %s", e)


async def _handle_optout(phone_raw: str, db: AsyncSession):
    """Mark patient as opted out."""
    from app.utils.phone_formatter import normalize_phone

    phone = normalize_phone(phone_raw)
    if not phone:
        return

    phone_encrypted = encryption_service.encrypt(phone)

    result = await db.execute(
        select(Patient).where(Patient.phone_encrypted == phone_encrypted)
    )
    patients = result.scalars().all()

    for patient in patients:
        patient.is_optout = True

    patient_ids = [p.id for p in patients]
    if patient_ids:
        from app.features.appointments.models import Appointment

        appt_result = await db.execute(
            select(Appointment.id).where(Appointment.patient_id.in_(patient_ids))
        )
        appt_ids = [row[0] for row in appt_result.fetchall()]

        if appt_ids:
            await db.execute(
                update(Reminder)
                .where(
                    Reminder.appointment_id.in_(appt_ids),
                    Reminder.status == ReminderStatus.PENDING,
                )
                .values(status=ReminderStatus.OPTOUT)
            )

    await db.flush()
    logger.info("Opted out %d patients, cancelled pending reminders", len(patients))


@router.post("/razorpay")
async def razorpay_webhook(request: Request):
    """Razorpay payment webhook — Phase V4 (payments)."""
    return JSONResponse(status_code=200, content={"status": "ok"})
