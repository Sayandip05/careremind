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
            to: Phone number (10-digit Indian)
            message: Message text
        Returns:
            {"success": True/False, "request_id": "...", "error": "..."}
        """
        if not self.is_configured:
            return {"success": False, "error": "SMS credentials not configured"}

        # Strip +91 if present
        phone = to.replace("+91", "").strip()

        headers = {
            "authorization": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "route": "q",  # Quick SMS (standard SMS)
            "message": message[:160],  # Truncate to SMS limit
            "language": "english",
            "flash": 0,
            "numbers": phone,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(FAST2SMS_URL, json=payload, headers=headers)

            data = response.json()

            if response.status_code == 200 and data.get("return"):
                request_id = data.get("request_id", "")
                logger.info("SMS sent to ...%s — request_id: %s", to[-4:], request_id)
                return {"success": True, "request_id": request_id}
            else:
                error = data.get("message", response.text)
                logger.warning("SMS failed to ...%s: %s", to[-4:], error)
                return {"success": False, "error": error}

        except httpx.TimeoutException:
            logger.error("SMS timeout sending to ...%s", to[-4:])
            return {"success": False, "error": "Request timeout"}

        except Exception as e:
            logger.error("SMS unexpected error: %s", e)
            return {"success": False, "error": str(e)}


sms_service = SMSService()
