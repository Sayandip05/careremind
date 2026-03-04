import httpx
from app.core.config import settings


class GroqService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY

    async def generate(self, prompt: str, language: str = "en"):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            return response.json()


groq_service = GroqService()
