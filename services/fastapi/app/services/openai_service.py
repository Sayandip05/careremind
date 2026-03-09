"""
OpenAI Service — Replaces Groq. Uses GPT-4o Mini for OCR text extraction
and structured data parsing from images.
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("careremind.services.openai")

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIService:
    """Wrapper for OpenAI ChatCompletion API with vision support."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4o-mini"

    async def chat(self, prompt: str, system: str = "") -> str:
        """Send a text-only chat request. Returns the assistant's response text."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        return await self._request(messages)

    async def vision(self, image_base64: str, prompt: str, system: str = "") -> str:
        """
        Send an image + prompt to GPT-4o Mini vision.
        image_base64: base64-encoded image string (no data URI prefix).
        Returns the assistant's response text.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})

        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}",
                        "detail": "high",
                    },
                },
            ],
        })

        return await self._request(messages)

    async def _request(self, messages: list[dict]) -> str:
        """Make the actual API call to OpenAI."""
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set — returning empty response")
            return ""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,  # Low temp for structured extraction
            "max_tokens": 4096,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OPENAI_CHAT_URL, json=payload, headers=headers)

            if response.status_code != 200:
                logger.error("OpenAI API error %d: %s", response.status_code, response.text)
                return ""

            data = response.json()
            return data["choices"][0]["message"]["content"]


openai_service = OpenAIService()
