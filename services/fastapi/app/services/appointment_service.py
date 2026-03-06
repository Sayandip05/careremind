"""
Appointment Service — Business logic for appointment CRUD.
Includes tenant ownership validation (IDOR protection).
"""

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.appointment import Appointment, UploadSource
from app.models.patient import Patient
from app.schemas.appointment import AppointmentCreate


async def create_appointment(
    tenant_id: str,
    data: AppointmentCreate,
    db: AsyncSession,
) -> Appointment:
    """
    Create a new appointment.
    IDOR protection: verifies the patient_id belongs to the requesting tenant.
    """
    # Ownership check — the golden rule
    result = await db.execute(
        select(Patient).where(Patient.id == data.patient_id)
    )
    patient = result.scalar_one_or_none()

    if not patient:
        raise NotFoundException("Patient not found")

    if str(patient.tenant_id) != str(tenant_id):
        raise ForbiddenException("Patient does not belong to your account")

    appointment = Appointment(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        patient_id=data.patient_id,
        visit_date=data.visit_date,
        next_visit_date=data.next_visit_date,
        specialty_override=data.specialty_override,
        notes_encrypted=data.notes,  # TODO: encrypt notes in Phase 3
        source=UploadSource(data.source),
    )
    db.add(appointment)
    await db.flush()
    return appointment


async def list_appointments(
    tenant_id: str,
    db: AsyncSession,
    patient_id: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Appointment], int]:
    """
    Paginated appointment list filtered by tenant_id.
    Optionally filtered by patient_id.
    """
    base_query = select(Appointment).where(Appointment.tenant_id == tenant_id)
    count_query = select(func.count(Appointment.id)).where(Appointment.tenant_id == tenant_id)

    if patient_id:
        base_query = base_query.where(Appointment.patient_id == patient_id)
        count_query = count_query.where(Appointment.patient_id == patient_id)

    # Count
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Fetch page
    offset = (page - 1) * per_page
    result = await db.execute(
        base_query
        .order_by(Appointment.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    appointments = list(result.scalars().all())

    return appointments, total
