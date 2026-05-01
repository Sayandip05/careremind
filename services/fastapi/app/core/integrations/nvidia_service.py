"""
NVIDIA Service — Uses google/gemma-3-27b-it via NVIDIA API
for OCR text extraction from patient register photos.
Supports inline base64 images directly (no asset upload needed).
Includes automatic retry with exponential backoff for transient failures.
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

logger = logging.getLogger("careremind.services.nvidia")

# Shared HTTP client (will be set by main.py lifespan)
_http_client: Optional[httpx.AsyncClient] = None

def set_http_client(client: httpx.AsyncClient):
    """Set the shared HTTP client for connection pooling."""
    global _http_client
    _http_client = client


class NvidiaService:
    """Wrapper for NVIDIA ChatCompletion API with vision support."""

    def __init__(self):
        self.api_key = settings.NVIDIA_API_KEY
        self.api_url = settings.NVIDIA_API_URL
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
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

        try:
            if _http_client:
                response = await _http_client.post(
                    self.api_url, json=payload, headers=headers,
                )
            else:
                async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_LONG) as client:
                    response = await client.post(
                        self.api_url, json=payload, headers=headers,
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

        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            logger.error("NVIDIA request error (after retries): %s", exc)
            return ""
        except Exception as exc:
            logger.error("NVIDIA unexpected error: %s", exc)
            return ""


nvidia_service = NvidiaService()
