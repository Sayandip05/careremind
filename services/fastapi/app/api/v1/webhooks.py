"""
Webhook routes — WhatsApp incoming messages and payment callbacks.
Handles opt-out (STOP) messages from patients.
"""

import logging

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import encryption_service
from app.models.patient import Patient
from app.models.reminder import Reminder, ReminderStatus
from app.utils.phone_formatter import normalize_phone

logger = logging.getLogger("careremind.api.webhooks")

router = APIRouter()

# Words that indicate opt-out
OPTOUT_KEYWORDS = {"stop", "unsubscribe", "cancel", "quit", "end", "band", "bnd"}


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
    # In production, verify hub_verify_token against a secret
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
    Primary use: handle opt-out (STOP) messages.
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=200, content={"status": "ok"})

    # Meta webhook payload structure
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                sender = message.get("from", "")
                text = (message.get("text", {}).get("body", "")).strip().lower()

                if not sender or not text:
                    continue

                # Check for opt-out keywords
                if text in OPTOUT_KEYWORDS:
                    await _handle_optout(sender, db)
                    logger.info("Opt-out processed for ...%s", sender[-4:])

    return JSONResponse(status_code=200, content={"status": "ok"})


async def _handle_optout(phone_raw: str, db: AsyncSession):
    """
    Mark patient as opted out.
    Finds patient by encrypted phone and sets is_optout = True.
    """
    phone = normalize_phone(phone_raw)
    if not phone:
        return

    phone_encrypted = encryption_service.encrypt(phone)

    # Find and update all patients with this phone (across tenants)
    result = await db.execute(
        select(Patient).where(Patient.phone_encrypted == phone_encrypted)
    )
    patients = result.scalars().all()

    for patient in patients:
        patient.is_optout = True

    # Cancel all pending reminders for opted-out patients
    patient_ids = [p.id for p in patients]
    if patient_ids:
        # Get appointment IDs for these patients
        from app.models.appointment import Appointment
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
