from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# ── Async Engine ─────────────────────────────────────────────
# Supabase PostgreSQL via asyncpg driver.
# The DATABASE_URL must use the "postgresql+asyncpg://" prefix.
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # detect stale connections
    echo=not settings.is_production,  # SQL logging in dev only
)

# ── Session Factory ──────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Alias for worker/scheduler tasks (used outside FastAPI Depends)
async_session = AsyncSessionLocal

# ── Declarative Base ─────────────────────────────────────────
Base = declarative_base()


# ── FastAPI Dependency ───────────────────────────────────────
async def get_db() -> AsyncSession:
    """
    Yields an async database session.
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
