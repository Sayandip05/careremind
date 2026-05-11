"""
WhatsApp Service — Sends messages via Meta Cloud API.
Production-grade with error handling, delivery status tracking, and automatic retry.
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

logger = logging.getLogger("careremind.services.whatsapp")

# Shared HTTP client (will be set by main.py lifespan)
_http_client: Optional[httpx.AsyncClient] = None


def set_http_client(client: httpx.AsyncClient):
    """Set the shared HTTP client for connection pooling."""
    global _http_client
    _http_client = client


class WhatsAppService:
    """Sends messages via Meta WhatsApp Cloud API."""

    @property
    def token(self) -> str:
        """Dynamically fetch the token at runtime to prevent freezing on initialization."""
        from app.core.config import settings

        return settings.META_WHATSAPP_TOKEN

    @property
    def _default_phone_number_id(self) -> str:
        from app.core.config import settings

        return settings.META_PHONE_NUMBER_ID

    @property
    def api_version(self) -> str:
        from app.core.config import settings

        return settings.META_WHATSAPP_API_VERSION

    @property
    def is_configured(self) -> bool:
        return bool(self.token and self._default_phone_number_id)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _send_request(
        self, url: str, payload: dict, headers: dict
    ) -> httpx.Response:
        """
        Internal method to send HTTP request with retry logic.
        Retries on timeout and network errors with exponential backoff.
        """
        if _http_client:
            return await _http_client.post(url, json=payload, headers=headers)
        else:
            async with httpx.AsyncClient(
                timeout=settings.HTTP_TIMEOUT_DEFAULT
            ) as client:
                return await client.post(url, json=payload, headers=headers)

    async def send_message(
        self, to: str, message: str, phone_number_id: Optional[str] = None
    ) -> dict:
        """
        Send a WhatsApp text message via Meta Cloud API.
        Args:
            to: Phone number in international format (e.g., +919876543210)
            message: Message text
            phone_number_id: Optional overlay to reply using a specific WhatsApp business number
        Returns:
            {"success": True/False, "message_id": "...", "error": "..."}
        """
        sender_id = phone_number_id or self._default_phone_number_id

        if not self.token or not sender_id:
            return {"success": False, "error": "WhatsApp credentials not configured"}

        url = f"https://graph.facebook.com/{self.api_version}/{sender_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }

        try:
            response = await self._send_request(url, payload, headers)
            data = response.json()

            if response.status_code == 200:
                msg_id = data.get("messages", [{}])[0].get("id", "")
                logger.info("WhatsApp sent to ...%s — message_id: %s", to[-4:], msg_id)
                return {"success": True, "message_id": msg_id}
            else:
                error = data.get("error", {}).get("message", response.text)
                logger.warning("WhatsApp failed to ...%s: %s", to[-4:], error)
                return {"success": False, "error": error}

        except httpx.TimeoutException:
            logger.error("WhatsApp timeout sending to ...%s (after retries)", to[-4:])
            return {"success": False, "error": "Request timeout after retries"}

        except Exception as e:
            logger.error("WhatsApp unexpected error: %s", e)
            return {"success": False, "error": str(e)}

    async def send_message_with_button(
        self,
        to: str,
        message: str,
        button_text: str,
        button_payload: str,
        phone_number_id: Optional[str] = None,
    ) -> dict:
        """
        Send a WhatsApp message with an interactive button.

        Args:
            to: Phone number in international format
            message: Message text
            button_text: Text displayed on button (e.g., "Book Next Visit")
            button_payload: Data sent back when button is clicked
            phone_number_id: Optional WhatsApp business number ID

        Returns:
            {"success": True/False, "message_id": "...", "error": "..."}
        """
        sender_id = phone_number_id or self._default_phone_number_id

        if not self.token or not sender_id:
            return {"success": False, "error": "WhatsApp credentials not configured"}

        url = f"https://graph.facebook.com/{self.api_version}/{sender_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": message},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {"id": button_payload, "title": button_text},
                        }
                    ]
                },
            },
        }

        try:
            response = await self._send_request(url, payload, headers)
            data = response.json()

            if response.status_code == 200:
                msg_id = data.get("messages", [{}])[0].get("id", "")
                logger.info(
                    "WhatsApp button message sent to ...%s — message_id: %s",
                    to[-4:],
                    msg_id,
                )
                return {"success": True, "message_id": msg_id}
            else:
                error = data.get("error", {}).get("message", response.text)
                logger.warning(
                    "WhatsApp button message failed to ...%s: %s", to[-4:], error
                )
                return {"success": False, "error": error}

        except httpx.TimeoutException:
            logger.error("WhatsApp timeout sending to ...%s (after retries)", to[-4:])
            return {"success": False, "error": "Request timeout after retries"}

        except Exception as e:
            logger.error("WhatsApp unexpected error: %s", e)
            return {"success": False, "error": str(e)}


whatsapp_service = WhatsAppService()
