from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    patient_id = Column(String, ForeignKey("patients.id"))
    visit_date = Column(DateTime)
    next_visit_date = Column(DateTime)
    specialty_override = Column(String)
    notes_encrypted = Column(String)
    source = Column(String)
    created_by_role = Column(String)
    created_at = Column(DateTime, server_default=func.now())
