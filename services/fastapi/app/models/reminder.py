import uuid
import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ReminderStatus(str, enum.Enum):
    PENDING = "Pending"
    SENT = "Sent"
    FAILED = "Failed"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    OPTOUT = "Optout"


class ChannelType(str, enum.Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    appointment_id = Column(String, ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False)
    reminder_number = Column(Integer, nullable=False, default=1)
    status = Column(Enum(ReminderStatus), nullable=False, default=ReminderStatus.PENDING)
    message_text = Column(Text)
    language_used = Column(String)
    channel = Column(Enum(ChannelType))
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True))
    error_log = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="reminders")
    appointment = relationship("Appointment", back_populates="reminders")
