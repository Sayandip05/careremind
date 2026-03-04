from sqlalchemy import Column, String, DateTime, Integer, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ReminderStatus(str, enum.Enum):
    PENDING = "Pending"
    SENT = "Sent"
    FAILED = "Failed"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    OPTOUT = "Optout"


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    appointment_id = Column(String, ForeignKey("appointments.id"))
    reminder_number = Column(Integer, default=1)
    status = Column(Enum(ReminderStatus), default=ReminderStatus.PENDING)
    message_text = Column(Text)
    language_used = Column(String)
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    error_log = Column(Text)
