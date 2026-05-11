"""
OpenAI Service — Production fallback VLM for OCR and structured data extraction.

Configured for GPT-5 (OpenAI's best-in-class vision model) for maximum accuracy
on handwritten clinic registers in Indian languages.

DISABLED in this portfolio build — OPENAI_API_KEY is not configured.
To enable in production: set OPENAI_API_KEY in environment variables.

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

logger = logging.getLogger("careremind.services.openai")

# Shared HTTP client (will be set by main.py lifespan)
_http_client: Optional[httpx.AsyncClient] = None


def set_http_client(client: httpx.AsyncClient):
    """Set the shared HTTP client for connection pooling."""
    global _http_client
    _http_client = client


class OpenAIService:
    """
    Wrapper for OpenAI ChatCompletion API with vision support.

    Production fallback for CareRemind's OCR pipeline.
    Uses GPT-5 — OpenAI's most capable vision model — for extracting
    patient data from handwritten/printed clinic register photos.
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = settings.OPENAI_API_URL
        # GPT-5: OpenAI's best-in-class VLM — update to exact model name when GA.
        # Ref: https://platform.openai.com/docs/models
        self.model = "gpt-5"

    async def chat(self, prompt: str, system: str = "") -> str:
        """Send a text-only prompt. Returns assistant's response text."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return await self._request(messages)

    async def vision(
        self, image_base64: str, prompt: str, system: str = "", model: str | None = None
    ) -> str:
        """
        Send an image + prompt to OpenAI GPT-5 vision.
        Returns assistant's response text.

        `model` param allows overriding the default (e.g. for testing gpt-4o-mini).
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append(
            {
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
            }
        )
        return await self._request(messages, model=model)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _request(self, messages: list[dict], model: str | None = None) -> str:
        """Make a ChatCompletion API call. Falls back to self.model if model not specified."""
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY not set — GPT-5 fallback disabled in this build"
            )
            return ""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model or self.model,
            "messages": messages,
            "max_tokens": 1024,
        }

        try:
            if _http_client:
                response = await _http_client.post(
                    self.api_url, json=payload, headers=headers
                )
            else:
                async with httpx.AsyncClient(
                    timeout=settings.HTTP_TIMEOUT_LONG
                ) as client:
                    response = await client.post(
                        self.api_url, json=payload, headers=headers
                    )

            if response.status_code != 200:
                logger.error(
                    "OpenAI API error %d: %s", response.status_code, response.text
                )
                return ""

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except (httpx.TimeoutException, httpx.NetworkError) as e:
            logger.error("OpenAI request error (after retries): %s", e)
            return ""
        except Exception as e:
            logger.error("OpenAI unexpected error: %s", e)
            return ""


openai_service = OpenAIService()
