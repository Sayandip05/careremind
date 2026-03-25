import uuid
import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PreferredChannel(str, enum.Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    BOTH = "both"


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    phone_encrypted = Column(String, nullable=False)
    preferred_channel = Column(Enum(PreferredChannel), nullable=False, default=PreferredChannel.WHATSAPP)
    has_whatsapp = Column(Boolean, default=None)
    language_preference = Column(String)
    is_optout = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
