"""
Booking service — business logic for patient self-booking.
"""

import logging
from datetime import date, datetime, time, timedelta, timezone
from typing import List, Optional
import uuid

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.booking.models import Booking, BookingStatus, DailySchedule, PaymentStatus
from app.features.clinics.models import ClinicLocation
from app.features.patients.models import Patient

logger = logging.getLogger("careremind.services.booking")

# Slot configuration
SLOT_DURATION_MINUTES = 30
CLINIC_START_TIME = time(9, 0)  # 9:00 AM
CLINIC_END_TIME = time(17, 0)   # 5:00 PM
MAX_BOOKINGS_PER_SLOT = 1
RESERVATION_EXPIRY_MINUTES = 10


class BookingService:
    """Handles all booking-related business logic."""

    @staticmethod
    async def get_available_slots(
        db: AsyncSession,
        clinic_location_id: str,
        booking_date: date,
    ) -> List[dict]:
        """
        Get available slots for a specific clinic and date.
        
        Returns list of slots with availability status.
        """
        # Validate date (must be tomorrow, not today or past)
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        if booking_date < tomorrow:
            return []  # No same-day or past bookings
        
        # Generate all possible slots
        slots = BookingService._generate_time_slots()
        
        # Fetch existing bookings for this date and clinic
        result = await db.execute(
            select(Booking.slot_time, func.count(Booking.id).label("count"))
            .where(
                and_(
                    Booking.clinic_location_id == clinic_location_id,
                    Booking.booking_date == booking_date,
                    Booking.status.in_([BookingStatus.RESERVED, BookingStatus.CONFIRMED])
                )
            )
            .group_by(Booking.slot_time)
        )
        
        booked_slots = {row[0]: row[1] for row in result.fetchall()}
        
        # Mark availability
        available_slots = []
        for slot_time in slots:
            booking_count = booked_slots.get(slot_time, 0)
            available_slots.append({
                "slot_time": slot_time,
                "is_available": booking_count < MAX_BOOKINGS_PER_SLOT,
                "booking_count": booking_count,
            })
        
        return available_slots

    @staticmethod
    def _generate_time_slots() -> List[time]:
        """Generate all time slots for the day."""
        slots = []
        current = datetime.combine(date.today(), CLINIC_START_TIME)
        end = datetime.combine(date.today(), CLINIC_END_TIME)
        
        while current < end:
            slots.append(current.time())
            current += timedelta(minutes=SLOT_DURATION_MINUTES)
        
        return slots

    @staticmethod
    async def reserve_slot(
        db: AsyncSession,
        tenant_id: str,
        patient_id: str,
        clinic_location_id: str,
        booking_date: date,
        slot_time: time,
    ) -> Optional[Booking]:
        """
        Reserve a slot for 10 minutes (temporary hold).
        
        Returns Booking object if successful, None if slot unavailable.
        
        Race condition protection: Database unique constraint prevents double-booking.
        """
        from sqlalchemy.exc import IntegrityError
        
        # Validate date
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        if booking_date < tomorrow:
            logger.warning("Attempted same-day booking for %s", booking_date)
            return None
        
        # Check if slot is available (advisory check, not authoritative)
        result = await db.execute(
            select(func.count(Booking.id))
            .where(
                and_(
                    Booking.clinic_location_id == clinic_location_id,
                    Booking.booking_date == booking_date,
                    Booking.slot_time == slot_time,
                    Booking.status.in_([BookingStatus.RESERVED, BookingStatus.CONFIRMED])
                )
            )
        )
        
        existing_count = result.scalar()
        
        if existing_count >= MAX_BOOKINGS_PER_SLOT:
            logger.info("Slot %s on %s is full", slot_time, booking_date)
            return None
        
        # Create reservation
        booking = Booking(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            patient_id=patient_id,
            clinic_location_id=clinic_location_id,
            booking_date=booking_date,
            slot_time=slot_time,
            status=BookingStatus.RESERVED,
            payment_status=PaymentStatus.PENDING,
            amount=200.00,  # Default consultation fee
        )
        
        booking.set_expiry(RESERVATION_EXPIRY_MINUTES)
        
        try:
            db.add(booking)
            await db.flush()
            
            logger.info(
                "Reserved slot %s on %s for patient %s (expires in %d min)",
                slot_time, booking_date, patient_id, RESERVATION_EXPIRY_MINUTES
            )
            
            return booking
            
        except IntegrityError as e:
            # Race condition: Another user booked this slot simultaneously
            # Database constraint prevented double-booking
            logger.info(
                "Slot %s on %s already booked (race condition caught by DB constraint)",
                slot_time, booking_date
            )
            await db.rollback()
            return None

    @staticmethod
    async def confirm_booking(
        db: AsyncSession,
        booking_id: str,
        razorpay_payment_id: str,
        razorpay_order_id: str,
    ) -> Optional[Booking]:
        """
        Confirm a booking after successful payment.
        
        Returns updated Booking object.
        """
        result = await db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()
        
        if not booking:
            logger.error("Booking %s not found", booking_id)
            return None
        
        if booking.status != BookingStatus.RESERVED:
            logger.warning("Booking %s is not in RESERVED status", booking_id)
            return None
        
        if booking.is_expired():
            logger.warning("Booking %s has expired", booking_id)
            booking.status = BookingStatus.EXPIRED
            await db.flush()
            return None
        
        # Update booking
        booking.status = BookingStatus.CONFIRMED
        booking.payment_status = PaymentStatus.COMPLETED
        booking.razorpay_payment_id = razorpay_payment_id
        booking.razorpay_order_id = razorpay_order_id
        booking.confirmed_at = datetime.now(timezone.utc)
        
        await db.flush()
        
        logger.info("Confirmed booking %s with payment %s", booking_id, razorpay_payment_id)
        
        return booking

    @staticmethod
    async def cancel_booking(
        db: AsyncSession,
        booking_id: str,
        tenant_id: str,
    ) -> Optional[Booking]:
        """
        Cancel a booking.
        
        Returns updated Booking object.
        """
        result = await db.execute(
            select(Booking).where(
                and_(
                    Booking.id == booking_id,
                    Booking.tenant_id == tenant_id
                )
            )
        )
        booking = result.scalar_one_or_none()
        
        if not booking:
            return None
        
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
            return booking
        
        booking.status = BookingStatus.CANCELLED
        await db.flush()
        
        logger.info("Cancelled booking %s", booking_id)
        
        return booking

    @staticmethod
    async def cleanup_expired_reservations(db: AsyncSession) -> int:
        """
        Find and cancel expired reservations.
        
        Returns count of cancelled bookings.
        """
        now = datetime.now(timezone.utc)
        
        result = await db.execute(
            select(Booking).where(
                and_(
                    Booking.status == BookingStatus.RESERVED,
                    Booking.expires_at < now
                )
            )
        )
        
        expired_bookings = result.scalars().all()
        
        for booking in expired_bookings:
            booking.status = BookingStatus.EXPIRED
        
        await db.flush()
        
        logger.info("Cleaned up %d expired reservations", len(expired_bookings))
        
        return len(expired_bookings)

    @staticmethod
    async def assign_serial_numbers(
        db: AsyncSession,
        clinic_location_id: str,
        schedule_date: date,
    ) -> int:
        """
        Assign serial numbers to confirmed bookings for a specific date.
        Called at midnight during PDF generation.
        
        Returns count of bookings assigned.
        """
        result = await db.execute(
            select(Booking)
            .where(
                and_(
                    Booking.clinic_location_id == clinic_location_id,
                    Booking.booking_date == schedule_date,
                    Booking.status == BookingStatus.CONFIRMED,
                    Booking.serial_number.is_(None)
                )
            )
            .order_by(Booking.confirmed_at)
        )
        
        bookings = result.scalars().all()
        
        for idx, booking in enumerate(bookings, start=1):
            booking.serial_number = idx
        
        await db.flush()
        
        logger.info(
            "Assigned serial numbers to %d bookings for %s at clinic %s",
            len(bookings), schedule_date, clinic_location_id
        )
        
        return len(bookings)

    @staticmethod
    async def get_daily_bookings(
        db: AsyncSession,
        clinic_location_id: str,
        schedule_date: date,
    ) -> List[Booking]:
        """
        Get all confirmed bookings for a specific date and clinic.
        Used for PDF generation.
        """
        result = await db.execute(
            select(Booking)
            .where(
                and_(
                    Booking.clinic_location_id == clinic_location_id,
                    Booking.booking_date == schedule_date,
                    Booking.status == BookingStatus.CONFIRMED
                )
            )
            .order_by(Booking.serial_number, Booking.slot_time)
        )
        
        return result.scalars().all()

