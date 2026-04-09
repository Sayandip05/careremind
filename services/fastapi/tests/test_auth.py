"""
Tests for authentication endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_tenant(client: AsyncClient, sample_tenant_data):
    """Test tenant registration."""
    response = await client.post("/api/v1/auth/register", json=sample_tenant_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "tenant" in data
    assert data["tenant"]["email"] == sample_tenant_data["email"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, sample_tenant_data):
    """Test registration with duplicate email."""
    # First registration
    await client.post("/api/v1/auth/register", json=sample_tenant_data)
    
    # Second registration with same email
    response = await client.post("/api/v1/auth/register", json=sample_tenant_data)
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, sample_tenant_data):
    """Test successful login."""
    # Register first
    await client.post("/api/v1/auth/register", json=sample_tenant_data)
    
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": sample_tenant_data["email"],
            "password": sample_tenant_data["password"],
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, sample_tenant_data):
    """Test login with invalid credentials."""
    # Register first
    await client.post("/api/v1/auth/register", json=sample_tenant_data)
    
    # Login with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": sample_tenant_data["email"],
            "password": "WrongPassword123!",
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, sample_tenant_data):
    """Test getting current user profile."""
    # Register and get token
    register_response = await client.post("/api/v1/auth/register", json=sample_tenant_data)
    token = register_response.json()["access_token"]
    
    # Get profile
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_tenant_data["email"]
    assert data["doctor_name"] == sample_tenant_data["doctor_name"]


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing protected endpoint without token."""
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 403

