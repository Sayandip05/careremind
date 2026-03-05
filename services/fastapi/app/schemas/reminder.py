from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReminderResponse(BaseModel):
    """Schema for reminder data in API responses."""
    id: str
    appointment_id: str
    reminder_number: int
    status: str
    message_text: Optional[str]
    language_used: Optional[str]
    channel: Optional[str]
    scheduled_at: datetime
    sent_at: Optional[datetime]
    error_log: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ReminderListResponse(BaseModel):
    """Paginated reminder list."""
    reminders: list[ReminderResponse]
    total: int
    page: int
    per_page: int
