from cryptography.fernet import Fernet
from app.core.config import settings


class SecurityService:
    def __init__(self):
        self.key = (
            settings.FIELD_ENCRYPTION_KEY.encode()
            if settings.FIELD_ENCRYPTION_KEY
            else Fernet.generate_key()
        )
        self.cipher = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        return self.cipher.decrypt(data.encode()).decode()

    def hash_password(self, password: str) -> str:
        import hashlib

        return hashlib.sha256(password.encode()).hexdigest()


security = SecurityService()
