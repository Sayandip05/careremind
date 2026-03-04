from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PlanEnum(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True)
    clinic_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    specialty = Column(String)
    language_preference = Column(String, default="english")
    whatsapp_number = Column(String)
    plan = Column(Enum(PlanEnum), default=PlanEnum.FREE)
    trial_ends_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
