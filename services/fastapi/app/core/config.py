from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/careremind"
    REDIS_URL: str = "redis://localhost:6379"
    JWT_SECRET_KEY: str = "change-me"
    JWT_EXPIRY_HOURS: int = 24
    FIELD_ENCRYPTION_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    META_WHATSAPP_TOKEN: str = ""
    META_PHONE_NUMBER_ID: str = ""
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_SECRET: str = ""
    STORAGE_BACKEND: str = "local"
    VISION_BACKEND: str = "google"
    GOOGLE_VISION_KEY: str = ""
    SENTRY_DSN: str = ""


settings = Settings()
