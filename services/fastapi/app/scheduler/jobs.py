"""
Scheduled jobs — Midnight PDF generation and expired reservation cleanup.

Uses distributed locking to prevent duplicate execution across multiple instances.
"""

import logging
from datetime import date, datetime, timedelta, timezone
import uuid
from contextlib import asynccontextmanager

from sqlalchemy import and_, select

from app.core.database import async_session
from app.core.integrations.whatsapp_service import whatsapp_service
from app.core.pdf_generator import pdf_generator
from app.features.auth.models import Tenant
from app.features.booking.models import DailySchedule
from app.features.booking.service import BookingService
from app.features.clinics.models import ClinicLocation

logger = logging.getLogger("careremind.scheduler")


@asynccontextmanager
async def distributed_lock(lock_name: str, timeout: int = 300):
    """
    Distributed lock using Redis to prevent duplicate job execution across instances.
    
    Args:
        lock_name: Unique name for the lock
        timeout: Lock expiry time in seconds (auto-release if job crashes)
    
    Yields:
        bool: True if lock acquired, False if already held by another instance
    """
    from app.core.cache import cache
    
    lock_key = f"scheduler_lock:{lock_name}"
    lock_value = str(uuid.uuid4())
    
    # Try to acquire lock (SET NX = set if not exists)
    try:
        client = cache.client
        if not client:
            # Redis not available, run job anyway (fail-open)
            logger.warning("Redis unavailable, running job without lock")
            yield True
            return
        
        acquired = await client.set(
            lock_key,
            lock_value,
            nx=True,  # Only set if key doesn't exist
            ex=timeout  # Auto-expire after timeout
        )
        
        if not acquired:
            logger.info("Lock '%s' already held by another instance, skipping job", lock_name)
            yield False
            return
        
        logger.info("Acquired lock '%s'", lock_name)
        yield True
        
    finally:
        # Release lock only if we still own it (atomic check-and-delete)
        if client and acquired:
            try:
                # Lua script for atomic release
                release_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                await client.eval(release_script, 1, lock_key, lock_value)
                logger.info("Released lock '%s'", lock_name)
            except Exception as e:
                logger.warning("Failed to release lock '%s': %s", lock_name, e)


async def generate_daily_schedules_job():
    """
    Midnight job (12:00 AM IST) — Generate daily appointment PDFs.
    
    Uses distributed locking to ensure only one instance runs this job.
    
    For each active clinic location:
    1. Assign serial numbers to confirmed bookings
    2. Fetch all bookings for today
    3. Generate PDF with online bookings + walk-in slots
    4. Save to database
    5. Send PDF to doctor's WhatsApp
    """
    async with distributed_lock("generate_daily_schedules", timeout=600) as acquired:
        if not acquired:
            return  # Another instance is already running this job
        
        logger.info("Starting daily schedule generation job")
    
    today = date.today()
    
    async with async_session() as db:
        try:
            # Fetch all active clinic locations
            result = await db.execute(
                select(ClinicLocation).where(ClinicLocation.is_active.is_(True))
            )
            clinics = result.scalars().all()
            
            logger.info("Found %d active clinic locations", len(clinics))
            
            for clinic in clinics:
                try:
                    # Assign serial numbers
                    assigned_count = await BookingService.assign_serial_numbers(
                        db, clinic.id, today
                    )
                    
                    # Fetch bookings for today
                    bookings = await BookingService.get_daily_bookings(
                        db, clinic.id, today
                    )
                    
                    # Load tenant
                    tenant_result = await db.execute(
                        select(Tenant).where(Tenant.id == clinic.tenant_id)
                    )
                    tenant = tenant_result.scalar_one_or_none()
                    
                    if not tenant:
                        logger.error("Tenant not found for clinic %s", clinic.id)
                        continue
                    
                    # Generate PDF
                    pdf_url = await pdf_generator.generate_daily_schedule(
                        schedule_date=today,
                        clinic_name=clinic.clinic_name,
                        doctor_name=tenant.doctor_name,
                        bookings=bookings,
                        walk_in_slots=10,
                        tenant_id=clinic.tenant_id,
                        clinic_location_id=clinic.id,
                    )
                    
                    if not pdf_url:
                        logger.error("Failed to generate PDF for clinic %s", clinic.id)
                        continue
                    
                    # Save to database
                    schedule = DailySchedule(
                        id=str(uuid.uuid4()),
                        tenant_id=clinic.tenant_id,
                        clinic_location_id=clinic.id,
                        schedule_date=today,
                        pdf_url=pdf_url,
                        total_online_bookings=len(bookings),
                        total_walk_in_slots=10,
                        generated_at=datetime.now(timezone.utc),
                    )
                    db.add(schedule)
                    
                    # Send to doctor's WhatsApp
                    if tenant.whatsapp_number and whatsapp_service.is_configured:
                        message = (
                            f"📋 Daily Schedule - {today.strftime('%d %B %Y')}\n\n"
                            f"Clinic: {clinic.clinic_name}\n"
                            f"Online Bookings: {len(bookings)}\n"
                            f"Walk-in Slots: 10\n\n"
                            f"PDF: {pdf_url}"
                        )
                        
                        result = await whatsapp_service.send_message(
                            to=tenant.whatsapp_number,
                            message=message,
                        )
                        
                        if result.get("success"):
                            schedule.sent_at = datetime.now(timezone.utc)
                            logger.info("Sent schedule PDF to doctor %s", tenant.id)
                        else:
                            logger.warning(
                                "Failed to send schedule to doctor %s: %s",
                                tenant.id, result.get("error")
                            )
                    
                    logger.info(
                        "Generated schedule for clinic %s: %d bookings",
                        clinic.clinic_name, len(bookings)
                    )
                    
                except Exception as e:
                    logger.error(
                        "Failed to generate schedule for clinic %s: %s",
                        clinic.id, e, exc_info=True
                    )
                    continue
            
            await db.commit()
            logger.info("Daily schedule generation completed")
            
        except Exception as e:
            logger.error("Daily schedule generation failed: %s", e, exc_info=True)
            await db.rollback()


async def cleanup_expired_reservations_job():
    """
    Periodic job (every 5 minutes) — Cancel expired reservations.
    
    Uses distributed locking to prevent duplicate execution.
    
    Finds all bookings with status=RESERVED and expires_at < now,
    then updates status to EXPIRED.
    """
    async with distributed_lock("cleanup_expired_reservations", timeout=120) as acquired:
        if not acquired:
            return  # Another instance is already running this job
        
        logger.info("Starting expired reservation cleanup job")
    
    async with async_session() as db:
        try:
            cancelled_count = await BookingService.cleanup_expired_reservations(db)
            await db.commit()
            
            if cancelled_count > 0:
                logger.info("Cleaned up %d expired reservations", cancelled_count)
            
        except Exception as e:
            logger.error("Expired reservation cleanup failed: %s", e, exc_info=True)
            await db.rollback()


# Scheduler configuration (to be used with APScheduler)
SCHEDULED_JOBS = [
    {
        "func": generate_daily_schedules_job,
        "trigger": "cron",
        "hour": 0,
        "minute": 0,
        "id": "generate_daily_schedules",
        "name": "Generate Daily Schedules (Midnight)",
        "replace_existing": True,
    },
    {
        "func": cleanup_expired_reservations_job,
        "trigger": "interval",
        "minutes": 5,
        "id": "cleanup_expired_reservations",
        "name": "Cleanup Expired Reservations (Every 5 min)",
        "replace_existing": True,
    },
]

