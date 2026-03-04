from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class MessageTemplate(Base):
    __tablename__ = "message_templates"

    id = Column(String, primary_key=True)
    tenant_id = Column(String)
    specialty = Column(String)
    language = Column(String)
    template_name = Column(String)
    meta_template_id = Column(String)
    body = Column(String)
    is_active = Column(Boolean, default=True)
