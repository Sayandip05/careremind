from app.core.security import security


class EncryptionService:
    def encrypt_field(self, value: str) -> str:
        return security.encrypt(value)

    def decrypt_field(self, value: str) -> str:
        return security.decrypt(value)


encryption_service = EncryptionService()
