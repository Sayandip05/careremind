import os
from pathlib import Path


class StorageService:
    def __init__(self):
        self.backend = os.getenv("STORAGE_BACKEND", "local")
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)

    async def save(self, filename: str, data: bytes):
        path = self.upload_dir / filename
        path.write_bytes(data)
        return str(path)

    async def delete(self, filename: str):
        path = self.upload_dir / filename
        if path.exists():
            path.unlink()


storage = StorageService()
