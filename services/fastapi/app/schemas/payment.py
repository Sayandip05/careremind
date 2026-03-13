from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PaymentBase(BaseModel):
    amount: int
    plan: str
    status: str
    razorpay_order_id: str
    razorpay_payment_id: Optional[str] = None


class PaymentCreate(PaymentBase):
    tenant_id: str


class PaymentResponse(PaymentBase):
    id: str
    tenant_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
