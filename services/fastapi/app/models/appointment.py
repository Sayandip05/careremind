import uuid
import enum
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UploadSource(str, enum.Enum):
    EXCEL = "excel"
    PHOTO = "photo"
    MANUAL = "manual"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(String, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    visit_date = Column(Date, nullable=False)
    next_visit_date = Column(Date)
    specialty_override = Column(String)
    notes_encrypted = Column(Text)
    source = Column(Enum(UploadSource), nullable=False, default=UploadSource.MANUAL)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
    reminders = relationship("Reminder", back_populates="appointment", cascade="all, delete-orphan")
