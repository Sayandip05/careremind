from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String)
    user_id = Column(String)
    role = Column(String)
    action = Column(String)
    resource = Column(String)
    resource_id = Column(String)
    ip_address = Column(String)
    user_agent = Column(String)
    old_value_encrypted = Column(Text)
    new_value_encrypted = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
