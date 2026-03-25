import httpx
from app.core.config import settings


class VisionService:
    def __init__(self):
        self.api_key = settings.GOOGLE_VISION_KEY

    async def extract_text(self, image_data: bytes):
        return {"text": ""}


vision_service = VisionService()
