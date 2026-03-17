"""
Tests for health check and security utilities.
"""

import pytest
from httpx import AsyncClient

from app.core.security import (
    create_access_token,
    verify_access_token,
    verify_password,
    get_password_hash,
    encryption_service,
)


@pytest.mark.asyncio
class TestHealthCheck:
    """GET /health"""

    async def test_health_returns_200(self, client: AsyncClient):
        """Health endpoint is always accessible."""
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "careremind-api"


class TestPasswordHashing:
    """Bcrypt password hashing."""

    def test_hash_and_verify(self):
        """Hashed password can be verified."""
        password = "MySecurePassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails(self):
        """Wrong password fails verification."""
        hashed = get_password_hash("CorrectPassword")
        assert verify_password("WrongPassword", hashed) is False

    def test_different_hashes(self):
        """Same password produces different hashes (bcrypt salt)."""
        hash1 = get_password_hash("SamePassword")
        hash2 = get_password_hash("SamePassword")
        assert hash1 != hash2  # Different salt each time


class TestJWT:
    """JWT token creation and verification."""

    def test_create_and_verify(self):
        """Token can be created and verified."""
        token = create_access_token("tenant-123", "test@example.com")
        payload = verify_access_token(token)
        assert payload["sub"] == "tenant-123"
        assert payload["email"] == "test@example.com"

    def test_invalid_token_raises(self):
        """Invalid token raises HTTPException."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            verify_access_token("invalid.token.here")
        assert exc_info.value.status_code == 401


class TestEncryption:
    """AES-256 field encryption for patient PII."""

    def test_encrypt_and_decrypt(self):
        """Encrypted text can be decrypted back to original."""
        plaintext = "9876543210"
        encrypted = encryption_service.encrypt(plaintext)
        assert encrypted != plaintext
        decrypted = encryption_service.decrypt(encrypted)
        assert decrypted == plaintext

    def test_different_ciphertexts(self):
        """Same plaintext produces different ciphertexts (Fernet uses random IV)."""
        text = "SamePhoneNumber"
        enc1 = encryption_service.encrypt(text)
        enc2 = encryption_service.encrypt(text)
        assert enc1 != enc2  # Different IV each time

    def test_decrypt_wrong_key_fails(self):
        """Decrypting with wrong key fails."""
        from cryptography.fernet import InvalidToken, Fernet
        other_cipher = Fernet(Fernet.generate_key())
        encrypted = other_cipher.encrypt(b"secret")
        with pytest.raises(InvalidToken):
            encryption_service.decrypt(encrypted.decode())
