"""
Dedup Agent — Checks extracted patient rows against existing patients
in the database using encrypted phone comparison.
"""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encryption_service
from app.models.patient import Patient

logger = logging.getLogger("careremind.agents.dedup")

ExtractedRow = dict[str, Any]


class DedupAgent:
    """Deduplicates patient rows against the database."""

    async def deduplicate(
        self,
        rows: list[ExtractedRow],
        tenant_id: str,
        db: AsyncSession,
    ) -> dict:
        """
        Takes extracted rows with normalized phones.
        Returns {new: [...], duplicates: [...]}.

        Dedup logic:
        1. Encrypt each phone
        2. Batch-fetch existing encrypted phones for this tenant
        3. Split into new vs duplicate
        """
        if not rows:
            return {"new": [], "duplicates": []}

        # Build a lookup of encrypted_phone → row
        phone_to_row: dict[str, ExtractedRow] = {}
        for row in rows:
            encrypted = encryption_service.encrypt(row["phone"])
            row["_phone_encrypted"] = encrypted  # Stash for later use
            phone_to_row[encrypted] = row

        # Batch-fetch existing patients for this tenant
        encrypted_phones = list(phone_to_row.keys())
        result = await db.execute(
            select(Patient.phone_encrypted).where(
                Patient.tenant_id == tenant_id,
                Patient.phone_encrypted.in_(encrypted_phones),
            )
        )
        existing_phones = {row[0] for row in result.fetchall()}

        # Split
        new_rows: list[ExtractedRow] = []
        dup_rows: list[ExtractedRow] = []

        for encrypted, row in phone_to_row.items():
            if encrypted in existing_phones:
                dup_rows.append(row)
            else:
                new_rows.append(row)

        logger.info(
            "Dedup result: %d new, %d duplicates (out of %d)",
            len(new_rows), len(dup_rows), len(rows),
        )

        return {"new": new_rows, "duplicates": dup_rows}
