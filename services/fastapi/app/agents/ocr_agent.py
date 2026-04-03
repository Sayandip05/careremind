"""
OCR Agent — Extracts patient data from photos of patient registers.
Primary: NVIDIA Gemma-3-27b-it vision
Fallback: OpenAI GPT-4o Mini vision
"""

import base64
import json
import logging
from typing import Any

from app.core.integrations.nvidia_service import nvidia_service
from app.core.integrations.openai_service import openai_service
from app.utils.date_parser import parse_date
from app.utils.phone_formatter import normalize_phone

logger = logging.getLogger("careremind.agents.ocr")

ExtractedRow = dict[str, Any]

# System prompt for structured extraction
OCR_SYSTEM_PROMPT = """You are a data extraction assistant for an Indian medical clinic.
You will receive a photo of a patient register (handwritten or printed).

Extract ALL patient entries you can see. For each patient, extract:
- name: Patient's full name
- phone: Phone number (10-digit Indian mobile)
- visit_date: Date of visit (if visible)
- next_visit_date: Next appointment / follow-up date (if visible)

Return ONLY a JSON array. Example:
[
  {"name": "Ramesh Kumar", "phone": "9876543210", "visit_date": "15/03/2025", "next_visit_date": "15/04/2025"},
  {"name": "Sita Devi", "phone": "8765432109", "visit_date": "15/03/2025", "next_visit_date": null}
]

Rules:
- If you cannot read a field, set it to null
- Phone numbers should be digits only, no +91 prefix
- Dates in DD/MM/YYYY format
- Return an empty array [] if no patients are visible
- Return ONLY the JSON array, no explanation text"""


class OcrAgent:
    """Extracts patient data from register photos.
    Primary: NVIDIA Gemma 3 | Fallback: OpenAI GPT-4o Mini
    """

    async def extract(self, image_bytes: bytes) -> dict:
        """
        Send image to vision API and parse the response.
        Tries NVIDIA first, falls back to OpenAI if NVIDIA fails.

        Returns:
            {
                "rows": [ExtractedRow, ...],
                "total_rows": int,
                "skipped": int,
                "errors": [str, ...],
                "raw_response": str,
                "provider": str,
            }
        """
        # Validate input
        if not image_bytes or len(image_bytes) < 100:
            return {
                "rows": [],
                "total_rows": 0,
                "skipped": 0,
                "errors": ["Invalid or empty image file"],
                "raw_response": "",
                "provider": "none",
            }
        
        errors: list[str] = []

        # Encode image to base64
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        # Try NVIDIA first
        provider = "nvidia"
        raw_response = await nvidia_service.vision(
            image_base64=image_b64,
            prompt="Extract all patient entries from this clinic register photo.",
            system=OCR_SYSTEM_PROMPT,
        )

        # Fallback to OpenAI if NVIDIA returned empty
        if not raw_response:
            logger.warning("NVIDIA returned empty — falling back to OpenAI")
            provider = "openai"
            raw_response = await openai_service.vision(
                image_base64=image_b64,
                prompt="Extract all patient entries from this clinic register photo.",
                system=OCR_SYSTEM_PROMPT,
            )

        if not raw_response:
            return {
                "rows": [],
                "total_rows": 0,
                "skipped": 0,
                "errors": ["Both NVIDIA and OpenAI returned empty — check API keys"],
                "raw_response": "",
                "provider": "none",
            }

        # Parse JSON response
        try:
            # Clean response — sometimes model wraps in ```json...```
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]  # Remove first line
                cleaned = cleaned.rsplit("```", 1)[0]  # Remove last ```
            cleaned = cleaned.strip()

            raw_rows = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse OCR JSON: %s\nRaw: %s", e, raw_response[:500])
            return {
                "rows": [],
                "total_rows": 0,
                "skipped": 0,
                "errors": [f"Could not parse AI response as JSON: {e}"],
                "raw_response": raw_response,
                "provider": provider,
            }

        if not isinstance(raw_rows, list):
            return {
                "rows": [],
                "total_rows": 0,
                "skipped": 0,
                "errors": ["AI response is not a list"],
                "raw_response": raw_response,
                "provider": provider,
            }

        # Normalize each row
        extracted: list[ExtractedRow] = []
        skipped = 0

        for i, row in enumerate(raw_rows):
            if not isinstance(row, dict):
                skipped += 1
                continue

            name = (row.get("name") or "").strip()
            raw_phone = str(row.get("phone") or "").strip()

            if not name:
                skipped += 1
                errors.append(f"OCR row {i + 1}: missing name")
                continue

            phone = normalize_phone(raw_phone) if raw_phone else None
            if not phone:
                skipped += 1
                errors.append(f"OCR row {i + 1}: invalid phone '{raw_phone}' for '{name}'")
                continue

            extracted.append({
                "name": name,
                "phone": phone,
                "visit_date": parse_date(row.get("visit_date")),
                "next_visit_date": parse_date(row.get("next_visit_date")),
            })

        logger.info(
            "OCR extraction (%s): %d rows extracted, %d skipped, %d errors",
            provider, len(extracted), skipped, len(errors),
        )

        return {
            "rows": extracted,
            "total_rows": len(extracted) + skipped,
            "skipped": skipped,
            "errors": errors,
            "raw_response": raw_response,
            "provider": provider,
        }
