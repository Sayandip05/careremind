from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    All values have sensible defaults for local development.
    In production, set these via .env file or environment variables.
    """

    # ── Environment ──────────────────────────────────────────
    ENVIRONMENT: str = "development"  # development | staging | production

    # ── Database (Supabase PostgreSQL) ───────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/careremind"

    # ── Supabase (Storage & SDK) ─────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""  # service_role key for backend

    # ── Cache & Queue ────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"

    # ── Authentication ───────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production-minimum-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    
    # ── Social OAuth Logins ──────────────────────────────────
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    FACEBOOK_CLIENT_ID: str = ""
    FACEBOOK_CLIENT_SECRET: str = ""

    # ── Patient Data Encryption ──────────────────────────────
    FIELD_ENCRYPTION_KEY: str = ""

    # ── AI — Message Generation ──────────────────────────────
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # ── WhatsApp (Meta Cloud API) ────────────────────────────
    META_WHATSAPP_TOKEN: str = ""
    META_PHONE_NUMBER_ID: str = ""

    # ── SMS Fallback ─────────────────────────────────────────
    FAST2SMS_API_KEY: str = ""

    # ── Vision OCR ───────────────────────────────────────────
    VISION_BACKEND: str = "nvidia"  # nvidia | openai | textract
    NVIDIA_API_KEY: str = ""
    GOOGLE_VISION_KEY: str = ""

    # ── Storage ──────────────────────────────────────────────
    STORAGE_BACKEND: str = "supabase"  # supabase | s3 | local

    # ── AWS (leave empty until migration) ────────────────────
    AWS_S3_BUCKET: str = ""
    AWS_ACCESS_KEY: str = ""
    AWS_SECRET_KEY: str = ""
    AWS_TEXTRACT_REGION: str = ""

    # ── Payments (V2 — Booking) ─────────────────────────────
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""

    # ── API Base URL (for OAuth callbacks) ───────────────────
    API_BASE_URL: str = "http://localhost:8000"

    # ── CORS ─────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3002"

    # ── Monitoring ───────────────────────────────────────────
    SENTRY_DSN: str = ""

    # ── Database Pool ────────────────────────────────────────
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
