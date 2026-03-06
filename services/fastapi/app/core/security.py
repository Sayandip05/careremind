from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

# ── JWT Tokens ───────────────────────────────────────────────
def create_access_token(tenant_id: str, email: str) -> str:
    """
    Create a signed JWT containing the tenant_id and email.
    Token expires after JWT_EXPIRY_HOURS (default 24h).
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRY_HOURS)
    payload = {
        "sub": tenant_id,
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_access_token(token: str) -> dict:
    """
    Decode and validate a JWT. Returns the payload dict.
    Raises HTTPException 401 if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("sub") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
        )


# ── Field Encryption (Patient PII) ──────────────────────────
class EncryptionService:
    """AES-256 encryption for sensitive patient fields (phone numbers, notes)."""

    def __init__(self):
        key = settings.FIELD_ENCRYPTION_KEY
        if key:
            # Ensure the key is valid Fernet format
            self._cipher = Fernet(key.encode() if isinstance(key, str) else key)
        else:
            # Auto-generate for development — NOT safe for production
            self._cipher = Fernet(Fernet.generate_key())

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string. Returns base64-encoded ciphertext."""
        return self._cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext. Returns plaintext."""
        return self._cipher.decrypt(ciphertext.encode()).decode()


encryption_service = EncryptionService()


# ── Auth Dependency ──────────────────────────────────────────
bearer_scheme = HTTPBearer()


async def get_current_tenant(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> "Tenant":
    """
    FastAPI dependency that:
    1. Extracts the Bearer token from the Authorization header
    2. Validates the JWT
    3. Loads the Tenant from the database
    4. Returns the Tenant object

    Usage: tenant: Tenant = Depends(get_current_tenant)
    """
    # Import here to avoid circular imports at module level
    from app.models.tenant import Tenant

    payload = verify_access_token(credentials.credentials)
    tenant_id = payload["sub"]

    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id, Tenant.is_active.is_(True))
    )
    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found or deactivated",
        )

    return tenant
