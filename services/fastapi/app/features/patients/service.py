"""
Patient Service — Business logic for patient CRUD operations.
Handles phone encryption, deduplication, and tenant ownership validation.
"""

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.core.security import encryption_service
from app.features.patients.models import Patient, PreferredChannel
from app.features.patients.schemas import PatientCreate, PatientUpdate


async def create_patient(
    tenant_id: str,
    data: PatientCreate,
    db: AsyncSession,
) -> Patient:
    """
    Create a new patient with encrypted phone number.
    Checks for duplicates using deterministic phone hash + tenant_id.
    """
    # Generate hash and encrypt phone
    phone_hash = encryption_service.hash_phone(data.phone)
    phone_encrypted = encryption_service.encrypt(data.phone)

    # Dedup check — same phone hash + same tenant = duplicate
    existing = await db.execute(
        select(Patient).where(
            Patient.tenant_id == tenant_id,
            Patient.phone_hash == phone_hash,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictException("Patient with this phone number already exists")

    patient = Patient(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        name=data.name,
        phone_encrypted=phone_encrypted,
        phone_hash=phone_hash,
        preferred_channel=PreferredChannel(data.preferred_channel),
        language_preference=data.language_preference,
    )
    db.add(patient)
    await db.flush()  # populate defaults before returning
    return patient


async def list_patients(
    tenant_id: str,
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Patient], int]:
    """
    Paginated patient list filtered by tenant_id.
    Returns (patients, total_count).
    """
    # Count
    count_result = await db.execute(
        select(func.count(Patient.id)).where(Patient.tenant_id == tenant_id)
    )
    total = count_result.scalar() or 0

    # Fetch page
    offset = (page - 1) * per_page
    result = await db.execute(
        select(Patient)
        .where(Patient.tenant_id == tenant_id)
        .order_by(Patient.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    patients = list(result.scalars().all())

    return patients, total


async def get_patient(
    tenant_id: str,
    patient_id: str,
    db: AsyncSession,
) -> Patient:
    """
    Get a single patient by ID.
    IDOR protection: verifies patient belongs to the requesting tenant.
    """
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()

    if not patient:
        raise NotFoundException("Patient not found")

    if str(patient.tenant_id) != str(tenant_id):
        raise ForbiddenException("Patient does not belong to your account")

    return patient


async def update_patient(
    tenant_id: str,
    patient_id: str,
    data: PatientUpdate,
    db: AsyncSession,
) -> Patient:
    """
    Update a patient. Only provided fields are updated.
    IDOR protection: verifies patient belongs to the requesting tenant.
    Re-encrypts phone if changed.
    """
    patient = await get_patient(tenant_id, patient_id, db)

    if data.name is not None:
        patient.name = data.name

    if data.phone is not None:
        patient.phone_encrypted = encryption_service.encrypt(data.phone)
        patient.phone_hash = encryption_service.hash_phone(data.phone)

    if data.preferred_channel is not None:
        patient.preferred_channel = PreferredChannel(data.preferred_channel)

    if data.language_preference is not None:
        patient.language_preference = data.language_preference

    await db.flush()
    return patient


async def delete_patient(
    tenant_id: str,
    patient_id: str,
    db: AsyncSession,
) -> None:
    """
    Delete a patient and all associated appointments and reminders.
    IDOR protection: verifies patient belongs to the requesting tenant.
    Cascades delete via SQLAlchemy relationships.
    """
    patient = await get_patient(tenant_id, patient_id, db)
    
    await db.delete(patient)
    await db.flush()
