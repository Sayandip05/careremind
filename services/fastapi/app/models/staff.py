from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class StaffRole(str, enum.Enum):
    DOCTOR = "doctor"
    RECEPTIONIST = "receptionist"
    ADMIN = "admin"


class Staff(Base):
    __tablename__ = "staff"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(StaffRole), default=StaffRole.RECEPTIONIST)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
