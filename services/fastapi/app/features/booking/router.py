"""
Booking routes — Patient self-booking API endpoints.
"""

import logging
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.integrations.razorpay_service import razorpay_service
from app.core.pdf_generator import pdf_generator
from app.core.security import get_current_tenant, get_current_tenant_flexible
from app.features.auth.models import Tenant
from app.features.booking.models import Booking, BookingStatus, DailySchedule
from app.features.booking.schemas import (
    BookingResponse,
    CancelBookingRequest,
    ClinicLocationResponse,
    ConfirmBookingRequest,
    ConfirmBookingResponse,
    DailyScheduleResponse,
    ReserveSlotRequest,
    ReserveSlotResponse,
    SlotResponse,
)
from app.features.booking.service import BookingService
from app.features.clinics.models import ClinicLocation
from app.features.patients.models import Patient

logger = logging.getLogger("careremind.api.booking")

router = APIRouter()


@router.get("/clinics", response_model=List[ClinicLocationResponse])
async def get_clinic_locations(
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all active clinic locations for the current tenant.
    Used when patient needs to select a clinic for booking.
    """
    result = await db.execute(
        select(ClinicLocation).where(
            and_(
                ClinicLocation.tenant_id == str(tenant.id),
                ClinicLocation.is_active.is_(True),
            )
        )
    )

    clinics = result.scalars().all()
    return clinics


@router.get("/slots", response_model=List[SlotResponse])
async def get_available_slots(
    clinic_location_id: str = Query(..., description="Clinic location ID"),
    booking_date: date = Query(..., description="Date to check (YYYY-MM-DD)"),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Get available time slots for a specific clinic and date.

    Rules:
    - Only next-day booking allowed (no same-day)
    - Returns slots from 9 AM to 5 PM (30-min intervals)
    """
    # Verify clinic belongs to tenant
    result = await db.execute(
        select(ClinicLocation).where(
            and_(
                ClinicLocation.id == clinic_location_id,
                ClinicLocation.tenant_id == str(tenant.id),
            )
        )
    )
    clinic = result.scalar_one_or_none()

    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic location not found")

    # Validate date (must be tomorrow or later)
    today = date.today()
    tomorrow = today + timedelta(days=1)

    if booking_date < tomorrow:
        raise HTTPException(
            status_code=400,
            detail="Only next-day booking allowed. No same-day booking.",
        )

    # Get available slots
    slots = await BookingService.get_available_slots(
        db, clinic_location_id, booking_date
    )

    return slots


@router.post("/reserve", response_model=ReserveSlotResponse)
async def reserve_slot(
    request: ReserveSlotRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Reserve a slot for 10 minutes (temporary hold).
    Creates a Razorpay order for payment.

    Flow:
    1. Reserve slot (status=RESERVED, expires in 10 min)
    2. Create Razorpay order
    3. Return order details for payment
    """
    # Verify patient belongs to tenant
    result = await db.execute(
        select(Patient).where(
            and_(Patient.id == request.patient_id, Patient.tenant_id == str(tenant.id))
        )
    )
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Reserve slot
    booking = await BookingService.reserve_slot(
        db,
        tenant_id=str(tenant.id),
        patient_id=request.patient_id,
        clinic_location_id=request.clinic_location_id,
        booking_date=request.booking_date,
        slot_time=request.slot_time,
    )

    if not booking:
        raise HTTPException(
            status_code=409, detail="Slot no longer available or invalid date"
        )

    logger.info(
        "Slot reserved: booking_id=%s, patient_id=%s, clinic=%s, date=%s, time=%s, expires_at=%s",
        booking.id,
        booking.patient_id,
        booking.clinic_location_id,
        booking.booking_date,
        booking.slot_time,
        booking.expires_at,
    )

    # Create Razorpay order
    razorpay_result = await razorpay_service.create_order(
        amount=float(booking.amount),
        receipt=f"booking_{booking.id}",
        notes={
            "booking_id": booking.id,
            "patient_id": patient.id,
            "tenant_id": str(tenant.id),
        },
    )

    if not razorpay_result.get("success"):
        # Cancel reservation if payment order creation failed
        await BookingService.cancel_booking(db, booking.id, str(tenant.id))
        await db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Payment gateway error: {razorpay_result.get('error')}",
        )

    # Update booking with Razorpay order ID
    booking.razorpay_order_id = razorpay_result["order_id"]
    await db.commit()
    await db.refresh(booking)

    # Calculate expiry time in seconds
    from datetime import datetime, timezone

    expires_in = int((booking.expires_at - datetime.now(timezone.utc)).total_seconds())

    return ReserveSlotResponse(
        booking=BookingResponse.from_orm(booking),
        razorpay_order_id=razorpay_result["order_id"],
        razorpay_key_id=razorpay_service.key_id,
        amount=float(booking.amount),
        currency="INR",
        expires_in_seconds=max(0, expires_in),
    )


@router.post("/confirm", response_model=ConfirmBookingResponse)
async def confirm_booking(
    request: ConfirmBookingRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm a booking after successful payment.

    Flow:
    1. Verify payment signature
    2. Update booking status to CONFIRMED
    3. Generate PDF bill
    4. Return confirmation
    """
    # Verify booking belongs to tenant
    result = await db.execute(
        select(Booking).where(
            and_(Booking.id == request.booking_id, Booking.tenant_id == str(tenant.id))
        )
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Verify payment signature
    is_valid = razorpay_service.verify_payment_signature(
        razorpay_order_id=request.razorpay_order_id,
        razorpay_payment_id=request.razorpay_payment_id,
        razorpay_signature=request.razorpay_signature,
    )

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    # Confirm booking
    confirmed_booking = await BookingService.confirm_booking(
        db,
        booking_id=request.booking_id,
        razorpay_payment_id=request.razorpay_payment_id,
        razorpay_order_id=request.razorpay_order_id,
    )

    if not confirmed_booking:
        raise HTTPException(
            status_code=400, detail="Booking expired or already confirmed"
        )

    await db.commit()
    await db.refresh(confirmed_booking)

    logger.info(
        "Booking confirmed: booking_id=%s, payment_id=%s, amount=%.2f, serial_number=%s",
        confirmed_booking.id,
        confirmed_booking.razorpay_payment_id,
        float(confirmed_booking.amount),
        confirmed_booking.serial_number or "pending",
    )

    # Load relationships for PDF generation
    await db.refresh(confirmed_booking, ["patient", "clinic_location"])

    # Generate PDF bill
    pdf_url = await pdf_generator.generate_patient_bill(
        booking=confirmed_booking,
        patient_name=confirmed_booking.patient.name,
        doctor_name=tenant.doctor_name,
        clinic_name=confirmed_booking.clinic_location.clinic_name,
    )

    return ConfirmBookingResponse(
        booking=BookingResponse.from_orm(confirmed_booking),
        message=f"Booking confirmed! Serial #{confirmed_booking.serial_number or 'Pending'}. See you on {confirmed_booking.booking_date.strftime('%d %B')} at {confirmed_booking.slot_time.strftime('%I:%M %p')}.",
        pdf_bill_url=pdf_url,
    )


@router.post("/cancel")
async def cancel_booking(
    request: CancelBookingRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel a booking.
    """
    booking = await BookingService.cancel_booking(
        db, request.booking_id, str(tenant.id)
    )

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    await db.commit()

    logger.info("Booking cancelled: booking_id=%s, tenant_id=%s", booking.id, tenant.id)

    return {
        "message": "Booking cancelled successfully",
        "booking_id": booking.id,
    }


@router.get("/schedule/{schedule_date}", response_model=DailyScheduleResponse)
async def get_daily_schedule(
    schedule_date: date,
    clinic_location_id: str = Query(..., description="Clinic location ID"),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the daily schedule PDF for a specific date and clinic.
    """
    result = await db.execute(
        select(DailySchedule).where(
            and_(
                DailySchedule.tenant_id == str(tenant.id),
                DailySchedule.clinic_location_id == clinic_location_id,
                DailySchedule.schedule_date == schedule_date,
            )
        )
    )

    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found for this date")

    return DailyScheduleResponse.from_orm(schedule)


@router.get("/list", response_model=List[dict])
async def list_bookings_for_date(
    booking_date: date = Query(
        default=None, description="Date to fetch (YYYY-MM-DD). Defaults to today."
    ),
    clinic_location_id: Optional[str] = Query(
        default=None, description="Filter by clinic location"
    ),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    List all confirmed bookings for a given date, enriched with patient name
    and clinic name. Defaults to today. Used by the doctor's Bookings dashboard.
    """
    from sqlalchemy.orm import selectinload

    target_date = booking_date or date.today()

    query = (
        select(Booking)
        .options(selectinload(Booking.patient), selectinload(Booking.clinic_location))
        .where(
            and_(
                Booking.tenant_id == str(tenant.id),
                Booking.booking_date == target_date,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]),
            )
        )
    )

    if clinic_location_id:
        query = query.where(Booking.clinic_location_id == clinic_location_id)

    query = query.order_by(Booking.slot_time)
    result = await db.execute(query)
    bookings = result.scalars().all()

    return [
        {
            "id": b.id,
            "serial_number": b.serial_number,
            "booking_date": b.booking_date.isoformat(),
            "slot_time": b.slot_time.strftime("%H:%M"),
            "slot_time_display": b.slot_time.strftime("%I:%M %p"),
            "patient_name": b.patient.name if b.patient else "Unknown",
            "clinic_name": b.clinic_location.clinic_name
            if b.clinic_location
            else "Unknown",
            "clinic_address": (
                f"{b.clinic_location.address_line}, {b.clinic_location.city}"
                if b.clinic_location
                else ""
            ),
            "clinic_location_id": b.clinic_location_id,
            "status": b.status,
            "payment_status": b.payment_status,
            "amount": float(b.amount),
            "confirmed_at": b.confirmed_at.isoformat() if b.confirmed_at else None,
        }
        for b in bookings
    ]


@router.get("/download-pdf")
async def download_schedule_pdf(
    booking_date: date = Query(..., description="Date for the schedule (YYYY-MM-DD)"),
    clinic_location_id: Optional[str] = Query(
        default=None, description="Clinic location ID"
    ),
    tenant: Tenant = Depends(get_current_tenant_flexible),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate and stream a daily schedule PDF for any given date.
    On-demand generation — does not require the midnight cron to have run.
    Streams directly as application/pdf for browser download.
    """
    from io import BytesIO
    from fastapi.responses import StreamingResponse
    from sqlalchemy.orm import selectinload

    query = (
        select(Booking)
        .options(selectinload(Booking.patient), selectinload(Booking.clinic_location))
        .where(
            and_(
                Booking.tenant_id == str(tenant.id),
                Booking.booking_date == booking_date,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]),
            )
        )
    )

    if clinic_location_id:
        query = query.where(Booking.clinic_location_id == clinic_location_id)

    query = query.order_by(Booking.serial_number.nulls_last(), Booking.slot_time)
    result = await db.execute(query)
    bookings = result.scalars().all()

    # Determine clinic name for PDF header
    clinic_label = "All Clinics"
    if clinic_location_id and bookings:
        first = bookings[0]
        if first.clinic_location:
            clinic_label = first.clinic_location.clinic_name
    elif clinic_location_id:
        # No bookings found but clinic specified — fetch clinic name
        clinic_result = await db.execute(
            select(ClinicLocation).where(
                and_(
                    ClinicLocation.id == clinic_location_id,
                    ClinicLocation.tenant_id == str(tenant.id),
                )
            )
        )
        clinic = clinic_result.scalar_one_or_none()
        clinic_label = clinic.clinic_name if clinic else "Unknown Clinic"

    # Generate PDF bytes in-memory (no storage upload)
    pdf_bytes = await pdf_generator.generate_daily_schedule_bytes(
        schedule_date=booking_date,
        clinic_name=clinic_label,
        doctor_name=tenant.doctor_name,
        bookings=bookings,
        walk_in_slots=10,
    )

    if not pdf_bytes:
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

    filename = f"schedule_{booking_date.isoformat()}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/my-bookings", response_model=List[BookingResponse])
async def get_my_bookings(
    patient_id: str = Query(..., description="Patient ID"),
    status: str = Query(None, description="Filter by status"),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all bookings for a specific patient.
    """
    query = select(Booking).where(
        and_(Booking.tenant_id == str(tenant.id), Booking.patient_id == patient_id)
    )

    if status:
        query = query.where(Booking.status == status)

    query = query.order_by(Booking.booking_date.desc(), Booking.slot_time.desc())

    result = await db.execute(query)
    bookings = result.scalars().all()

    return bookings
