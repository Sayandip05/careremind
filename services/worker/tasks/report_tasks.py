"""
Report tasks — generates daily summary for doctors.
Shows how many reminders were sent, failed, pending.
"""

import asyncio
import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger("careremind.worker.reports")


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(bind=True)
def generate_daily_summary(self, tenant_id: str = None):
    """
    Generate daily summary for a tenant or all tenants.
    Sends via WhatsApp to the doctor's registered number.
    """
    if tenant_id:
        return _run_async(_generate_for_tenant(tenant_id))
    else:
        return _run_async(_generate_for_all())


async def _generate_for_all():
    """Generate summaries for all active tenants."""
    from app.core.database import async_session
    from app.features.auth.models import Tenant
    from sqlalchemy import select

    async with async_session() as db:
        result = await db.execute(select(Tenant.id))
        tenant_ids = [row[0] for row in result.fetchall()]

    summaries = []
    for tid in tenant_ids:
        summary = await _generate_for_tenant(str(tid))
        summaries.append(summary)

    return {"tenants_processed": len(summaries), "summaries": summaries}


async def _generate_for_tenant(tenant_id: str):
    """Build and send daily summary for one tenant."""
    from app.core.database import async_session
    from app.features.reminders.models import Reminder, ReminderStatus
    from app.features.auth.models import Tenant
    from app.core.integrations.whatsapp_service import whatsapp_service
    from sqlalchemy import func, select, and_
    from datetime import datetime, timedelta, timezone

    async with async_session() as db:
        tenant = await db.get(Tenant, tenant_id)
        if not tenant:
            return {"tenant_id": tenant_id, "error": "Tenant not found"}

        today = date.today()

        # Count reminders by status for today
        counts = {}
        for status in ReminderStatus:
            result = await db.execute(
                select(func.count()).select_from(Reminder).where(
                    Reminder.tenant_id == tenant_id,
                    Reminder.status == status,
                    func.date(Reminder.scheduled_at) == today,
                )
            )
            counts[status.value] = result.scalar() or 0

        # Build summary message
        message = (
            f"📊 Daily Summary — {today.strftime('%d/%m/%Y')}\n\n"
            f"Dr. {tenant.doctor_name}, here's your reminder report:\n\n"
            f"✅ Sent: {counts.get('Sent', 0)}\n"
            f"⏳ Pending: {counts.get('Pending', 0)}\n"
            f"❌ Failed: {counts.get('Failed', 0)}\n"
            f"🚫 Opted-out: {counts.get('Optout', 0)}\n\n"
            f"Total reminders today: {sum(counts.values())}"
        )

        # Send to doctor's WhatsApp
        doctor_phone = tenant.whatsapp_number or tenant.phone
        if doctor_phone and whatsapp_service.is_configured:
            await whatsapp_service.send_message(doctor_phone, message)

    logger.info("Summary sent for tenant %s", tenant_id)
    return {"tenant_id": tenant_id, "counts": counts, "message": message}
