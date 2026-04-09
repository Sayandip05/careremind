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
    def is_configured(self) -> bool:
        return bool(self.token and self._default_phone_number_id)

    async def send_message(self, to: str, message: str, phone_number_id: Optional[str] = None) -> dict:
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

        url = f"https://graph.facebook.com/{META_API_VERSION}/{sender_id}/messages"
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
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)

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
            logger.error("WhatsApp timeout sending to ...%s", to[-4:])
            return {"success": False, "error": "Request timeout"}

        except Exception as e:
            logger.error("WhatsApp unexpected error: %s", e)
            return {"success": False, "error": str(e)}

    async def send_message_with_button(
        self,
        to: str,
        message: str,
        button_text: str,
        button_payload: str,
        phone_number_id: Optional[str] = None
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

        url = f"https://graph.facebook.com/{META_API_VERSION}/{sender_id}/messages"
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
                "body": {
                    "text": message
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": button_payload,
                                "title": button_text
                            }
                        }
                    ]
                }
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)

            data = response.json()

            if response.status_code == 200:
                msg_id = data.get("messages", [{}])[0].get("id", "")
                logger.info("WhatsApp button message sent to ...%s — message_id: %s", to[-4:], msg_id)
                return {"success": True, "message_id": msg_id}
            else:
                error = data.get("error", {}).get("message", response.text)
                logger.warning("WhatsApp button message failed to ...%s: %s", to[-4:], error)
                return {"success": False, "error": error}

        except httpx.TimeoutException:
            logger.error("WhatsApp timeout sending to ...%s", to[-4:])
            return {"success": False, "error": "Request timeout"}

        except Exception as e:
            logger.error("WhatsApp unexpected error: %s", e)
            return {"success": False, "error": str(e)}


whatsapp_service = WhatsAppService()
