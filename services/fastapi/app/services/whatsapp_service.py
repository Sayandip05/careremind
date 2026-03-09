"""
WhatsApp Service — Sends messages via Meta Cloud API.
Production-grade with error handling and delivery status tracking.
"""

import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger("careremind.services.whatsapp")

META_API_VERSION = "v21.0"


class WhatsAppService:
    """Sends messages via Meta WhatsApp Cloud API."""

    def __init__(self):
        self.token = settings.META_WHATSAPP_TOKEN
        self.phone_number_id = settings.META_PHONE_NUMBER_ID

    @property
    def is_configured(self) -> bool:
        return bool(self.token and self.phone_number_id)

    async def send_message(self, to: str, message: str) -> dict:
        """
        Send a text message via WhatsApp.

        Args:
            to: Phone number in international format (e.g., +919876543210)
            message: Message text

        Returns:
            {"success": True/False, "message_id": "...", "error": "..."}
        """
        if not self.is_configured:
            logger.warning("WhatsApp not configured — skipping send to %s", to[-4:])
            return {"success": False, "error": "WhatsApp credentials not configured"}

        # Strip + prefix — Meta API expects digits only
        phone = to.lstrip("+")

        url = f"https://graph.facebook.com/{META_API_VERSION}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {"preview_url": False, "body": message},
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)

            data = response.json()

            if response.status_code == 200:
                msg_id = data.get("messages", [{}])[0].get("id", "")
                logger.info("WhatsApp sent to ...%s — message_id: %s", to[-4:], msg_id)
                return {"success": True, "message_id": msg_id}
            else:
                error = data.get("error", {}).get("message", response.text)
                logger.error("WhatsApp send failed to ...%s: %s", to[-4:], error)
                return {"success": False, "error": error}

        except httpx.TimeoutException:
            logger.error("WhatsApp timeout sending to ...%s", to[-4:])
            return {"success": False, "error": "Request timeout"}

        except Exception as e:
            logger.error("WhatsApp unexpected error: %s", e)
            return {"success": False, "error": str(e)}


whatsapp_service = WhatsAppService()
