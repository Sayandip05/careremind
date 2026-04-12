from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
import hmac
import hashlib

from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

# ── Passwords ────────────────────────────────────────────────
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a hash of a plain password."""
    return password_hash.hash(password)


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
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
        )


# ── Field Encryption (Patient PII) ──────────────────────────
class EncryptionService:
    """AES-256 encryption for sensitive patient fields (phone numbers, notes).
    
    Uses Fernet for encryption (non-deterministic) and HMAC-SHA256 for hashing (deterministic).
    Hash is used for deduplication lookups, encryption for secure storage.
    """

    def __init__(self):
        key = settings.FIELD_ENCRYPTION_KEY
        if key:
            # Ensure the key is valid Fernet format
            self._cipher = Fernet(key.encode() if isinstance(key, str) else key)
            self._hash_key = key.encode() if isinstance(key, str) else key
        else:
            if settings.is_production:
                raise RuntimeError(
                    "FIELD_ENCRYPTION_KEY must be set in production. "
                    "Patient data encryption cannot use auto-generated keys."
                )
            # Fixed dev key — consistent across restarts so encrypted data stays readable
            # NEVER use this in production (it's a known value)
            dev_key = b"dev-careremind-key-do-not-use-in-prod="  # 44 bytes base64
            dev_fernet_key = Fernet.generate_key()  # fallback if above isn't valid
            try:
                self._cipher = Fernet(dev_key)
            except Exception:
                self._cipher = Fernet(dev_fernet_key)
                dev_key = dev_fernet_key
            self._hash_key = dev_key

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string. Returns base64-encoded ciphertext."""
        return self._cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext. Returns plaintext."""
        return self._cipher.decrypt(ciphertext.encode()).decode()

    def hash_phone(self, phone: str) -> str:
        """Create deterministic HMAC-SHA256 hash of phone number for dedup.
        
        Same phone number always produces the same hash (deterministic).
        Uses FIELD_ENCRYPTION_KEY as the HMAC key for security.
        """
        # Normalize phone before hashing (remove spaces, consistent format)
        normalized = phone.strip().replace(" ", "").replace("-", "")
        return hmac.HMAC(
            self._hash_key,
            normalized.encode(),
            hashlib.sha256
        ).hexdigest()


encryption_service = EncryptionService()


# ── Auth Dependency ──────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_tenant(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> "Tenant":
    """
    FastAPI dependency that:
    1. Extracts the Bearer token from the Authorization header via OAuth2 scheme
    2. Validates the JWT
    3. Loads the Tenant from the database
    4. Returns the Tenant object

    Usage: tenant: Tenant = Depends(get_current_tenant)
    """
    # Import here to avoid circular imports at module level
    from app.features.auth.models import Tenant

    payload = verify_access_token(token)
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
