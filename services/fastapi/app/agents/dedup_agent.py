"""
Dedup Agent — Checks extracted patient rows against existing patients
in the database using deterministic phone hash comparison.
"""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encryption_service
from app.features.patients.models import Patient

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
        1. Hash each phone (deterministic HMAC-SHA256)
        2. Encrypt each phone (Fernet for storage)
        3. Batch-fetch existing phone hashes for this tenant
        4. Split into new vs duplicate
        """
        if not rows:
            return {"new": [], "duplicates": []}

        # Build a lookup of phone_hash → row
        hash_to_row: dict[str, ExtractedRow] = {}
        for row in rows:
            phone = row["phone"]
            phone_hash = encryption_service.hash_phone(phone)
            phone_encrypted = encryption_service.encrypt(phone)
            row["_phone_hash"] = phone_hash  # Stash for later use
            row["_phone_encrypted"] = phone_encrypted  # Stash for later use
            hash_to_row[phone_hash] = row

        # Batch-fetch existing patients for this tenant by hash
        phone_hashes = list(hash_to_row.keys())
        result = await db.execute(
            select(Patient.phone_hash).where(
                Patient.tenant_id == tenant_id,
                Patient.phone_hash.in_(phone_hashes),
            )
        )
        existing_hashes = {row[0] for row in result.fetchall()}

        # Split
        new_rows: list[ExtractedRow] = []
        dup_rows: list[ExtractedRow] = []

        for phone_hash, row in hash_to_row.items():
            if phone_hash in existing_hashes:
                dup_rows.append(row)
            else:
                new_rows.append(row)

        logger.info(
            "Dedup result: %d new, %d duplicates (out of %d)",
            len(new_rows), len(dup_rows), len(rows),
        )

        return {"new": new_rows, "duplicates": dup_rows}
