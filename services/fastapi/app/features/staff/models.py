import uuid

from sqlalchemy import Column, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class StaffRole(str, enum.Enum):
    DOCTOR = "doctor"
    RECEPTIONIST = "receptionist"
    ADMIN = "admin"


class Staff(Base):
    __tablename__ = "staff"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(StaffRole), default=StaffRole.RECEPTIONIST)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="staff")
