import uuid
from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

import enum


class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_name = Column(String, nullable=False)
    clinic_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String)
    specialty = Column(String)
    language_preference = Column(String, nullable=False, default="english")
    whatsapp_number = Column(String)
    hashed_password = Column(String, nullable=False)
    email_marketing = Column(Boolean, nullable=False, default=True)
    plan = Column(Enum(PlanType), nullable=False, default=PlanType.FREE)
    trial_ends_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Clinic address fields
    street = Column(String)
    city = Column(String)
    pincode = Column(String)
    state = Column(String)

    # Relationships
    patients = relationship("Patient", back_populates="tenant", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="tenant", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="tenant", cascade="all, delete-orphan")
    upload_logs = relationship("UploadLog", back_populates="tenant", cascade="all, delete-orphan")
    staff = relationship("Staff", back_populates="tenant", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="tenant", cascade="all, delete-orphan")
    clinic_locations = relationship("ClinicLocation", back_populates="tenant", cascade="all, delete-orphan")
