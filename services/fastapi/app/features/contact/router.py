"""
Contact form endpoint — public, no auth required.
Stores inquiries and can optionally forward to email.
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

logger = logging.getLogger(__name__)

router = APIRouter()


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(default="", max_length=15)
    subject: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)


class ContactResponse(BaseModel):
    success: bool
    message: str


# In-memory store for now; swap with DB table when needed
_contact_submissions: list[dict] = []


@router.post("/", response_model=ContactResponse)
async def submit_contact(payload: ContactRequest):
    """
    Accept a contact form submission from the landing page.
    Public endpoint — no authentication required.
    """
    try:
        entry = {
            "name": payload.name,
            "email": payload.email,
            "phone": payload.phone,
            "subject": payload.subject,
            "message": payload.message,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }
        _contact_submissions.append(entry)
        logger.info("Contact form submitted by %s <%s>", payload.name, payload.email)

        return ContactResponse(
            success=True,
            message="Thank you for reaching out! We'll get back to you within 24 hours.",
        )
    except Exception as e:
        logger.error("Contact form error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to submit contact form.")
