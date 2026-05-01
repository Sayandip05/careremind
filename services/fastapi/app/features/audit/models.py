import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    """
    Append-only audit log. Records every create/update/delete action.
    Never deleted — used for compliance and debugging.
    """

    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="SET NULL"))
    user_id = Column(String)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    resource_id = Column(String)
    ip_address = Column(String)
    user_agent = Column(String)
    # Use JSON for SQLite compatibility, JSONB for PostgreSQL performance
    old_value = Column(JSON().with_variant(JSONB, "postgresql"))
    new_value = Column(JSON().with_variant(JSONB, "postgresql"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
