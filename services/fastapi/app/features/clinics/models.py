import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ClinicLocation(Base):
    """
    Clinic location model - supports multiple clinics per doctor.
    
    A doctor can have multiple clinic locations (e.g., "City Clinic", "Morning Clinic").
    Each location has its own address and can be managed independently.
    """
    __tablename__ = "clinic_locations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Clinic details
    clinic_name = Column(String, nullable=False)  # e.g., "City Clinic", "Morning Clinic"
    address_line = Column(String, nullable=False)  # Street address
    city = Column(String, nullable=False)
    pincode = Column(String(6), nullable=False)
    state = Column(String)
    
    # Contact
    phone = Column(String)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="clinic_locations")
    bookings = relationship("Booking", back_populates="clinic_location", cascade="all, delete-orphan")
    daily_schedules = relationship("DailySchedule", back_populates="clinic_location", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ClinicLocation(id={self.id}, name={self.clinic_name}, city={self.city})>"
