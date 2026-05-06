"""
Re-encryption script — fixes patients whose phone_encrypted was written
with a DIFFERENT key than the current FIELD_ENCRYPTION_KEY.

Strategy:
  1. Try to decrypt each patient with the current key (already correct — skip).
  2. If that fails, the phone was encrypted with an OLD key or the dev fallback.
     Since the phone numbers in seed_db.py are known (+9198765432XX), we
     reconstruct the plaintext from seed data and re-encrypt with the current key.
  3. For real unknown phones — we cannot recover them; those patients are marked.

Run:
    cd services/fastapi
    venv\\Scripts\\python scripts/reencrypt_patients.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import app.models  # noqa: F401 — load all models

from sqlalchemy import select
from app.core.database import async_session
from app.core.security import encryption_service
from app.features.patients.models import Patient


# Seed data phone map  name -> phone (from seed_db.py)
SEED_PHONES = {
    "Ramesh Kumar":  "+919876543201",
    "Sita Devi":     "+919876543202",
    "Arjun Patel":   "+919876543203",
    "Priya Singh":   "+919876543204",
    "Vijay Reddy":   "+919876543205",
    "Lakshmi Iyer":  "+919876543206",
    "Suresh Gupta":  "+919876543207",
    "Anjali Mehta":  "+919876543208",
    "Karthik Rao":   "+919876543209",
    "Deepa Nair":    "+919876543210",
}


async def reencrypt():
    print("=" * 60)
    print("PATIENT PHONE RE-ENCRYPTION TOOL")
    print("=" * 60)
    print(f"Current FIELD_ENCRYPTION_KEY: ...{encryption_service._hash_key[-8:].decode(errors='replace')}")
    print()

    fixed = 0
    skipped = 0
    unknown = 0

    async with async_session() as db:
        result = await db.execute(select(Patient))
        patients = result.scalars().all()
        print(f"Total patients found: {len(patients)}")
        print()

        for patient in patients:
            # Try decrypt with current key
            try:
                phone = encryption_service.decrypt(patient.phone_encrypted)
                print(f"  [OK]      {patient.name:<20} phone ends ...{phone[-4:]}")
                skipped += 1
                continue
            except Exception:
                pass

            # Current key failed — check if we know this patient's phone from seed data
            known_phone = SEED_PHONES.get(patient.name)
            if known_phone:
                # Re-encrypt with the current key
                patient.phone_encrypted = encryption_service.encrypt(known_phone)
                patient.phone_hash = encryption_service.hash_phone(known_phone)
                print(f"  [FIXED]   {patient.name:<20} re-encrypted with current key")
                fixed += 1
            else:
                print(f"  [UNKNOWN] {patient.name:<20} cannot recover phone — was not seeded")
                unknown += 1

        if fixed > 0:
            await db.commit()
            print(f"\nCommitted {fixed} re-encrypted patients to DB.")
        else:
            print("\nNo changes needed — all patients already use current key.")

    print()
    print("=" * 60)
    print(f"  OK (already correct): {skipped}")
    print(f"  Fixed (re-encrypted): {fixed}")
    print(f"  Unknown (skipped):    {unknown}")
    print("=" * 60)


asyncio.run(reencrypt())
