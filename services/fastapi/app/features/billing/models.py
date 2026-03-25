import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    razorpay_order_id = Column(String, nullable=False)
    razorpay_payment_id = Column(String)
    amount = Column(Integer, nullable=False)  # in paise
    plan = Column(String, nullable=False)
    status = Column(String, nullable=False)  # created, captured, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="payments")
