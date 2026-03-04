from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone_encrypted = Column(String)
    language_preference = Column(String)
    is_optout = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
