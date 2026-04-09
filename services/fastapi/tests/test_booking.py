"""
Tests for booking endpoints (V2 feature).
"""

from datetime import date, time, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.booking.models import Booking, BookingStatus
from app.features.booking.service import BookingService


@pytest.mark.asyncio
async def test_get_available_slots(
    client: AsyncClient,
    db_session: AsyncSession,
    sample_tenant_data
):
    """Test getting available slots for booking."""
    # Register and get token
    register_response = await client.post("/api/v1/auth/register", json=sample_tenant_data)
    token = register_response.json()["access_token"]
    tenant_id = register_response.json()["tenant"]["id"]
    
    # Create a clinic location first
    clinic_data = {
        "clinic_name": "Test Clinic",
        "address_line": "123 Test St",
        "city": "Mumbai",
        "pincode": "400001",
    }
    clinic_response = await client.post(
        "/api/v1/clinics",
        json=clinic_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    clinic_id = clinic_response.json()["id"]
    
    # Get slots for tomorrow
    tomorrow = date.today() + timedelta(days=1)
    response = await client.get(
        f"/api/v1/booking/slots?clinic_location_id={clinic_id}&booking_date={tomorrow}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    slots = response.json()
    assert len(slots) > 0
    assert all(slot["is_available"] for slot in slots)


@pytest.mark.asyncio
async def test_reserve_slot(db_session: AsyncSession):
    """Test slot reservation logic."""
    from app.features.auth.models import Tenant
    from app.features.patients.models import Patient
    from app.features.clinics.models import ClinicLocation
    import uuid
    
    # Create test data
    tenant = Tenant(
        id=str(uuid.uuid4()),
        doctor_name="Dr. Test",
        clinic_name="Test Clinic",
        email="test@test.com",
        hashed_password="hashed",
        specialty="general",
    )
    db_session.add(tenant)
    
    clinic = ClinicLocation(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        clinic_name="Test Clinic",
        address_line="123 Test St",
        city="Mumbai",
        pincode="400001",
    )
    db_session.add(clinic)
    
    patient = Patient(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        name="Test Patient",
        phone_encrypted="encrypted",
        phone_hash="hash",
    )
    db_session.add(patient)
    
    await db_session.commit()
    
    # Reserve a slot
    tomorrow = date.today() + timedelta(days=1)
    booking = await BookingService.reserve_slot(
        db=db_session,
        tenant_id=tenant.id,
        patient_id=patient.id,
        clinic_location_id=clinic.id,
        booking_date=tomorrow,
        slot_time=time(10, 0),
    )
    
    assert booking is not None
    assert booking.status == BookingStatus.RESERVED
    assert booking.expires_at is not None


@pytest.mark.asyncio
async def test_same_day_booking_rejected(db_session: AsyncSession):
    """Test that same-day booking is rejected."""
    from app.features.auth.models import Tenant
    from app.features.patients.models import Patient
    from app.features.clinics.models import ClinicLocation
    import uuid
    
    # Create test data
    tenant = Tenant(
        id=str(uuid.uuid4()),
        doctor_name="Dr. Test",
        clinic_name="Test Clinic",
        email="test@test.com",
        hashed_password="hashed",
        specialty="general",
    )
    db_session.add(tenant)
    
    clinic = ClinicLocation(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        clinic_name="Test Clinic",
        address_line="123 Test St",
        city="Mumbai",
        pincode="400001",
    )
    db_session.add(clinic)
    
    patient = Patient(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        name="Test Patient",
        phone_encrypted="encrypted",
        phone_hash="hash",
    )
    db_session.add(patient)
    
    await db_session.commit()
    
    # Try to book for today (should fail)
    today = date.today()
    booking = await BookingService.reserve_slot(
        db=db_session,
        tenant_id=tenant.id,
        patient_id=patient.id,
        clinic_location_id=clinic.id,
        booking_date=today,
        slot_time=time(10, 0),
    )
    
    assert booking is None


@pytest.mark.asyncio
async def test_cleanup_expired_reservations(db_session: AsyncSession):
    """Test cleanup of expired reservations."""
    from app.features.auth.models import Tenant
    from app.features.patients.models import Patient
    from app.features.clinics.models import ClinicLocation
    from datetime import datetime, timezone
    import uuid
    
    # Create test data
    tenant = Tenant(
        id=str(uuid.uuid4()),
        doctor_name="Dr. Test",
        clinic_name="Test Clinic",
        email="test@test.com",
        hashed_password="hashed",
        specialty="general",
    )
    db_session.add(tenant)
    
    clinic = ClinicLocation(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        clinic_name="Test Clinic",
        address_line="123 Test St",
        city="Mumbai",
        pincode="400001",
    )
    db_session.add(clinic)
    
    patient = Patient(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        name="Test Patient",
        phone_encrypted="encrypted",
        phone_hash="hash",
    )
    db_session.add(patient)
    
    # Create expired booking
    expired_booking = Booking(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        patient_id=patient.id,
        clinic_location_id=clinic.id,
        booking_date=date.today() + timedelta(days=1),
        slot_time=time(10, 0),
        status=BookingStatus.RESERVED,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),  # Already expired
    )
    db_session.add(expired_booking)
    
    await db_session.commit()
    
    # Run cleanup
    count = await BookingService.cleanup_expired_reservations(db_session)
    
    assert count == 1
    
    # Verify booking is now expired
    await db_session.refresh(expired_booking)
    assert expired_booking.status == BookingStatus.EXPIRED

