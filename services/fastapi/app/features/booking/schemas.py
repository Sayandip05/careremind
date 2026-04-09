from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.features.booking.models import BookingStatus, PaymentStatus


# ── Request Schemas ──────────────────────────────────────────


class SlotAvailabilityRequest(BaseModel):
    """Request to check available slots for a specific date and clinic."""
    clinic_location_id: str
    booking_date: date


class ReserveSlotRequest(BaseModel):
    """Request to reserve a slot (temporary hold for 10 minutes)."""
    clinic_location_id: str
    booking_date: date
    slot_time: time
    patient_id: str


class ConfirmBookingRequest(BaseModel):
    """Request to confirm a booking after payment."""
    booking_id: str
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


class CancelBookingRequest(BaseModel):
    """Request to cancel a booking."""
    booking_id: str
    reason: Optional[str] = None


# ── Response Schemas ─────────────────────────────────────────


class SlotResponse(BaseModel):
    """Available slot information."""
    slot_time: time
    is_available: bool
    booking_count: int = 0

    class Config:
        from_attributes = True


class ClinicLocationResponse(BaseModel):
    """Clinic location information for booking."""
    id: str
    clinic_name: str
    address_line: str
    city: str
    pincode: str
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class BookingResponse(BaseModel):
    """Booking information."""
    id: str
    tenant_id: str
    patient_id: str
    clinic_location_id: str
    booking_date: date
    slot_time: time
    serial_number: Optional[int] = None
    status: BookingStatus
    payment_status: PaymentStatus
    amount: float
    razorpay_order_id: Optional[str] = None
    reserved_at: datetime
    confirmed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReserveSlotResponse(BaseModel):
    """Response after reserving a slot."""
    booking: BookingResponse
    razorpay_order_id: str
    razorpay_key_id: str
    amount: float
    currency: str = "INR"
    expires_in_seconds: int


class ConfirmBookingResponse(BaseModel):
    """Response after confirming a booking."""
    booking: BookingResponse
    message: str
    pdf_bill_url: Optional[str] = None


class DailyScheduleResponse(BaseModel):
    """Daily schedule information."""
    id: str
    schedule_date: date
    pdf_url: Optional[str] = None
    total_online_bookings: int
    total_walk_in_slots: int
    generated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookingStatsResponse(BaseModel):
    """Booking statistics for dashboard."""
    total_bookings: int
    confirmed_bookings: int
    pending_bookings: int
    cancelled_bookings: int
    revenue_today: float
    revenue_this_month: float

