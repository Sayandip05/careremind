"""
Tests for AI agent pipeline.
"""

import pytest

from app.agents.excel_agent import ExcelAgent
from app.agents.dedup_agent import DedupAgent
from app.core.security import encryption_service


@pytest.mark.asyncio
async def test_excel_agent_valid_file():
    """Test Excel agent with valid file."""
    # Create a simple Excel file in memory
    from openpyxl import Workbook
    from io import BytesIO
    
    wb = Workbook()
    ws = wb.active
    
    # Add headers
    ws.append(["Name", "Phone", "Visit Date", "Next Visit"])
    
    # Add data
    ws.append(["John Doe", "9876543210", "2024-01-01", "2024-02-01"])
    ws.append(["Jane Smith", "9876543211", "2024-01-02", "2024-02-02"])
    
    # Save to bytes
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    file_bytes = buffer.read()
    
    # Test extraction
    agent = ExcelAgent()
    result = await agent.extract(file_bytes)
    
    assert result["total_rows"] == 2
    assert len(result["rows"]) == 2
    assert result["rows"][0]["name"] == "John Doe"
    assert result["rows"][0]["phone"] == "+919876543210"


@pytest.mark.asyncio
async def test_excel_agent_missing_columns():
    """Test Excel agent with missing required columns."""
    from openpyxl import Workbook
    from io import BytesIO
    
    wb = Workbook()
    ws = wb.active
    
    # Add headers without required columns
    ws.append(["Name", "Email"])
    ws.append(["John Doe", "john@example.com"])
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    file_bytes = buffer.read()
    
    agent = ExcelAgent()
    result = await agent.extract(file_bytes)
    
    assert len(result["errors"]) > 0
    assert "Missing required columns" in result["errors"][0]


@pytest.mark.asyncio
async def test_dedup_agent(db_session):
    """Test deduplication agent."""
    from app.features.auth.models import Tenant
    from app.features.patients.models import Patient
    import uuid
    
    # Create tenant
    tenant = Tenant(
        id=str(uuid.uuid4()),
        doctor_name="Dr. Test",
        clinic_name="Test Clinic",
        email="test@test.com",
        hashed_password="hashed",
        specialty="general",
    )
    db_session.add(tenant)
    
    # Create existing patient
    phone = "+919876543210"
    phone_hash = encryption_service.hash_phone(phone)
    phone_encrypted = encryption_service.encrypt(phone)
    
    existing_patient = Patient(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        name="Existing Patient",
        phone_encrypted=phone_encrypted,
        phone_hash=phone_hash,
    )
    db_session.add(existing_patient)
    await db_session.commit()
    
    # Test deduplication
    rows = [
        {"name": "Existing Patient", "phone": phone},  # Duplicate
        {"name": "New Patient", "phone": "+919876543211"},  # New
    ]
    
    agent = DedupAgent()
    result = await agent.deduplicate(rows, tenant.id, db_session)
    
    assert len(result["new"]) == 1
    assert len(result["duplicates"]) == 1
    assert result["new"][0]["name"] == "New Patient"
    assert result["duplicates"][0]["name"] == "Existing Patient"


def test_phone_hash_deterministic():
    """Test that phone hashing is deterministic."""
    phone = "+919876543210"
    
    hash1 = encryption_service.hash_phone(phone)
    hash2 = encryption_service.hash_phone(phone)
    
    assert hash1 == hash2


def test_phone_encryption_non_deterministic():
    """Test that phone encryption is non-deterministic."""
    phone = "+919876543210"
    
    encrypted1 = encryption_service.encrypt(phone)
    encrypted2 = encryption_service.encrypt(phone)
    
    # Different ciphertexts
    assert encrypted1 != encrypted2
    
    # But both decrypt to same value
    assert encryption_service.decrypt(encrypted1) == phone
    assert encryption_service.decrypt(encrypted2) == phone

