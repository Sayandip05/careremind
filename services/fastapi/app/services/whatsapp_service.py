import httpx
from app.core.config import settings


class WhatsAppService:
    def __init__(self):
        self.token = settings.META_WHATSAPP_TOKEN
        self.phone_number_id = settings.META_PHONE_NUMBER_ID

    async def send_message(self, to: str, message: str):
        url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            return response.json()


whatsapp_service = WhatsAppService()
