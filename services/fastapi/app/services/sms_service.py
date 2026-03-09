"""
SMS Service — Sends messages via Fast2SMS API (Indian SMS gateway).
Used as fallback when WhatsApp delivery fails.
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("careremind.services.sms")

FAST2SMS_URL = "https://www.fast2sms.com/dev/bulkV2"


class SMSService:
    """Sends SMS via Fast2SMS API."""

    def __init__(self):
        self.api_key = settings.FAST2SMS_API_KEY

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def send_message(self, to: str, message: str) -> dict:
        """
        Send an SMS via Fast2SMS.

        Args:
            to: Phone number in +91XXXXXXXXXX format
            message: Message text (max 160 chars for standard SMS)

        Returns:
            {"success": True/False, "request_id": "...", "error": "..."}
        """
        if not self.is_configured:
            logger.warning("Fast2SMS not configured — skipping SMS to ...%s", to[-4:])
            return {"success": False, "error": "SMS credentials not configured"}

        # Fast2SMS expects 10-digit Indian number without +91
        phone = to.lstrip("+")
        if phone.startswith("91") and len(phone) == 12:
            phone = phone[2:]

        headers = {
            "authorization": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "route": "q",  # Quick SMS route
            "message": message[:160],  # Truncate to SMS limit
            "language": "unicode",     # Support Hindi/Bengali etc.
            "numbers": phone,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(FAST2SMS_URL, json=payload, headers=headers)

            data = response.json()

            if data.get("return"):
                request_id = data.get("request_id", "")
                logger.info("SMS sent to ...%s — request_id: %s", to[-4:], request_id)
                return {"success": True, "request_id": request_id}
            else:
                error = data.get("message", response.text)
                logger.error("SMS send failed to ...%s: %s", to[-4:], error)
                return {"success": False, "error": error}

        except httpx.TimeoutException:
            logger.error("SMS timeout sending to ...%s", to[-4:])
            return {"success": False, "error": "Request timeout"}

        except Exception as e:
            logger.error("SMS unexpected error: %s", e)
            return {"success": False, "error": str(e)}


sms_service = SMSService()
