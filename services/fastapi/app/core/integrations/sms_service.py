"""
SMS Service — Sends messages via Fast2SMS API (Indian SMS gateway).
Used as fallback when WhatsApp delivery fails.
Includes automatic retry with exponential backoff.
"""

import logging
from typing import Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from app.core.config import settings

logger = logging.getLogger("careremind.services.sms")

# Shared HTTP client (will be set by main.py lifespan)
_http_client: Optional[httpx.AsyncClient] = None

def set_http_client(client: httpx.AsyncClient):
    """Set the shared HTTP client for connection pooling."""
    global _http_client
    _http_client = client


class SMSService:
    """Sends SMS via Fast2SMS API."""

    @property
    def api_key(self) -> str:
        """Get API key from settings (allows runtime config changes)."""
        return settings.FAST2SMS_API_KEY

    @property
    def api_url(self) -> str:
        """Get API URL from settings."""
        return settings.FAST2SMS_API_URL

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _send_request(self, url: str, payload: dict, headers: dict) -> httpx.Response:
        """
        Internal method to send HTTP request with retry logic.
        Retries on timeout and network errors with exponential backoff.
        """
        if _http_client:
            return await _http_client.post(url, json=payload, headers=headers)
        else:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_DEFAULT) as client:
                return await client.post(url, json=payload, headers=headers)

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

        # Truncate message to SMS limit with warning
        if len(message) > 160:
            logger.warning("SMS message truncated from %d to 160 chars for ...%s", len(message), to[-4:])
            message = message[:160]

        headers = {
            "authorization": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "route": "q",  # Quick SMS (standard SMS)
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": phone,
        }

        try:
            response = await self._send_request(self.api_url, payload, headers)
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
            logger.error("SMS timeout sending to ...%s (after retries)", to[-4:])
            return {"success": False, "error": "Request timeout after retries"}

        except Exception as e:
            logger.error("SMS unexpected error: %s", e)
            return {"success": False, "error": str(e)}


sms_service = SMSService()
