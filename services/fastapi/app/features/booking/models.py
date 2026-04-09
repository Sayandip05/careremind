import uuid
import enum
from datetime import datetime, timedelta, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Time, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class BookingStatus(str, enum.Enum):
    RESERVED = "reserved"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    EXPIRED = "expired"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Booking(Base):
    """
    Patient booking model - stores appointment bookings made via WhatsApp.
    
    Flow:
    1. Patient taps "Book Next Visit" in reminder
    2. Selects slot → status=RESERVED (10-min expiry)
    3. Completes payment → status=CONFIRMED
    4. At midnight → assigned serial_number
    5. After visit → status=COMPLETED
    """
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(String, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    appointment_id = Column(String, ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    clinic_location_id = Column(String, ForeignKey("clinic_locations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Booking details
    booking_date = Column(Date, nullable=False, index=True)
    slot_time = Column(Time, nullable=False)
    serial_number = Column(Integer)  # Assigned at midnight
    
    # Status
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.RESERVED, index=True)
    
    # Payment
    payment_id = Column(String)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    amount = Column(Numeric(10, 2), nullable=False, default=200.00)
    razorpay_order_id = Column(String)
    razorpay_payment_id = Column(String)
    
    # Timestamps
    reserved_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    confirmed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))  # 10 minutes from reserved_at
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="bookings")
    patient = relationship("Patient", back_populates="bookings")
    appointment = relationship("Appointment", back_populates="bookings")
    clinic_location = relationship("ClinicLocation", back_populates="bookings")

    def __repr__(self):
        return f"<Booking(id={self.id}, patient={self.patient_id}, date={self.booking_date}, status={self.status})>"

    def is_expired(self) -> bool:
        """Check if reservation has expired."""
        if self.status != BookingStatus.RESERVED:
            return False
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def set_expiry(self, minutes: int = 10):
        """Set expiry time for reservation."""
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)


class DailySchedule(Base):
    """
    Daily schedule model - stores generated PDFs for each clinic location.
    
    Generated at midnight (12:00 AM) with:
    - Online bookings at top (with serial numbers)
    - Walk-in slots at bottom
    """
    __tablename__ = "daily_schedules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    clinic_location_id = Column(String, ForeignKey("clinic_locations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Schedule details
    schedule_date = Column(Date, nullable=False, index=True)
    pdf_url = Column(String)
    
    # Stats
    total_online_bookings = Column(Integer, nullable=False, default=0)
    total_walk_in_slots = Column(Integer, nullable=False, default=10)
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="daily_schedules")
    clinic_location = relationship("ClinicLocation", back_populates="daily_schedules")

    def __repr__(self):
        return f"<DailySchedule(id={self.id}, date={self.schedule_date}, bookings={self.total_online_bookings})>"

