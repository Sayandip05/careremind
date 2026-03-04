from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReminderResponse(BaseModel):
    id: str
    appointment_id: str
    reminder_number: int
    status: str
    message_text: Optional[str]
    language_used: str
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
