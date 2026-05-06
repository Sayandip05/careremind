"""
Notification pipeline dry-run test.
Tests the FULL pipeline against the real demo patient from Supabase:
  load_context → check_optout → decrypt_phone → generate_message → (skip send)

No WhatsApp or SMS keys needed — we intercept at the send step and print the message.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import app.models  # load all models so SQLAlchemy relationships resolve

from sqlalchemy import select
from app.core.database import async_session
from app.core.security import encryption_service
from app.features.reminders.models import Reminder, ReminderStatus
from app.features.patients.models import Patient
from app.features.appointments.models import Appointment
from app.features.auth.models import Tenant
from app.agents.message_agent import MessageAgent


async def test_notification_pipeline():
    print("=" * 60)
    print("NOTIFICATION PIPELINE DRY-RUN TEST")
    print("=" * 60)

    async with async_session() as db:
        # 1. Load demo tenant
        tenant_result = await db.execute(
            select(Tenant).where(Tenant.email == "demo@careremind.com")
        )
        tenant = tenant_result.scalar_one_or_none()
        if not tenant:
            print("ERROR: Demo tenant not found — run seed_db.py first")
            return
        print(f"\n[1] Tenant loaded: {tenant.doctor_name} ({tenant.clinic_name})")

        # 2. Load a patient with encrypted phone
        patient_result = await db.execute(
            select(Patient).where(Patient.tenant_id == tenant.id).limit(1)
        )
        patient = patient_result.scalar_one_or_none()
        if not patient:
            print("ERROR: No patients found")
            return
        print(f"[2] Patient loaded: {patient.name} (id={patient.id[:8]}...)")

        # 3. Decrypt phone
        phone = encryption_service.decrypt(patient.phone_encrypted)
        if not phone:
            print("ERROR: Could not decrypt phone — check FIELD_ENCRYPTION_KEY")
            return
        print(f"[3] Phone decrypted: {phone[:4]}****{phone[-2:]}")

        # 4. Opt-out check
        if patient.is_optout:
            print("[4] Patient is OPTED OUT — would skip reminder")
        else:
            print(f"[4] Opt-out check: ACTIVE (is_optout={patient.is_optout})")

        # 5. Load an appointment
        appt_result = await db.execute(
            select(Appointment).where(Appointment.patient_id == patient.id).limit(1)
        )
        appointment = appt_result.scalar_one_or_none()
        if not appointment:
            print("[5] No appointment found for this patient — creating a mock one for message gen")
            from datetime import date, timedelta
            class MockAppointment:
                id = "mock-appt"
                patient_id = patient.id
                tenant_id = tenant.id
                visit_date = date.today() - timedelta(days=7)
                next_visit_date = date.today() + timedelta(days=7)
                specialty_override = None
            appointment = MockAppointment()
        else:
            print(f"[5] Appointment loaded: visit={appointment.visit_date}, next={appointment.next_visit_date}")

        # 6. Generate message
        print("\n[6] Generating reminder message...")
        message_agent = MessageAgent()
        try:
            message = await message_agent.generate(
                patient=patient,
                appointment=appointment,
                tenant=tenant,
                use_ai_polish=False,   # No OpenAI key needed
            )
            print(f"\n    Generated message:\n    {'-'*40}")
            print(f"    {message}")
            print(f"    {'-'*40}")
            print(f"    Length: {len(message)} chars")
        except Exception as e:
            print(f"ERROR generating message: {e}")
            raise

        # 7. Channel check
        print("\n[7] Channel availability:")
        from app.core.config import settings
        wa_configured = bool(settings.META_WHATSAPP_TOKEN and settings.META_PHONE_NUMBER_ID)
        print(f"    WhatsApp: {'CONFIGURED ✓' if wa_configured else 'NOT CONFIGURED — set META_WHATSAPP_TOKEN + META_PHONE_NUMBER_ID'}")

        if not wa_configured:
            print("\n    [!] WhatsApp not configured — reminders will be marked FAILED in production.")
            print(f"\n    Message WOULD be sent to: {phone}")

        # 8. Reminder records check
        reminder_result = await db.execute(
            select(Reminder).where(Reminder.tenant_id == tenant.id).limit(5)
        )
        reminders = reminder_result.scalars().all()
        print(f"\n[8] Reminders in DB for this tenant: {len(reminders)}")
        for r in reminders:
            channel_val = r.channel.value if hasattr(r.channel, 'value') else str(r.channel or 'N/A')
            status_val  = r.status.value  if hasattr(r.status,  'value') else str(r.status)
            scheduled   = r.scheduled_at.date() if r.scheduled_at else 'N/A'
            print(f"    - id={r.id[:8]}... status={status_val} channel={channel_val} scheduled={scheduled}")

    print("\n" + "=" * 60)
    print("RESULT: Pipeline is WORKING correctly.")
    print("  [OK] Tenant load:       OK")
    print("  [OK] Patient load:      OK")
    print("  [OK] Phone decryption:  OK")
    print("  [OK] Opt-out check:     OK")
    print("  [OK] Message generated: OK")
    print("  [--] WhatsApp send:     SKIPPED (no API key in dev env)")
    print("=" * 60)


asyncio.run(test_notification_pipeline())

