"""
NVIDIA Service — Uses google/gemma-3-27b-it via NVIDIA API
for OCR text extraction from patient register photos.
Supports inline base64 images directly (no asset upload needed).
"""

import logging
import httpx
from app.core.config import settings

logger = logging.getLogger("careremind.services.nvidia")

NVIDIA_CHAT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"


class NvidiaService:
    """Wrapper for NVIDIA ChatCompletion API with vision support."""

    def __init__(self):
        self.api_key = settings.NVIDIA_API_KEY
        self.model = "google/gemma-3-27b-it"

    async def vision(self, image_base64: str, prompt: str, system: str = "") -> str:
        """
        Send an image + prompt to NVIDIA vision model.
        Uses inline base64 image format.
        Returns assistant's response text.
        """
        if not self.api_key:
            logger.warning("NVIDIA_API_KEY not set — returning empty response")
            return ""

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
                    },
                },
            ],
        })

        return await self._request(messages)

    async def _request(self, messages: list[dict]) -> str:
        """Make a ChatCompletion API call to NVIDIA."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.20,
            "top_p": 0.70,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                response = await client.post(
                    NVIDIA_CHAT_URL, json=payload, headers=headers,
                )

                if response.status_code != 200:
                    logger.error(
                        "NVIDIA API error %d: %s",
                        response.status_code,
                        response.text,
                    )
                    return ""

                data = response.json()
                return data["choices"][0]["message"]["content"]

            except httpx.RequestError as exc:
                logger.error("NVIDIA request error: %s", exc)
                return ""


nvidia_service = NvidiaService()
