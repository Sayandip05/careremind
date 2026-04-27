"""
Alembic async environment -- connects to PostgreSQL via asyncpg
and discovers all models through the app.models shim.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.database import Base

# Import all models so Alembic can see them
import app.models  # noqa: F401  -- triggers the shim re-exports

# -- Alembic Config -----------------------------------------------------------
config = context.config

# Override sqlalchemy.url from settings (.env is the single source of truth)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata


# -- Offline Mode (generates SQL without connecting) --------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode -- emits SQL to stdout."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# -- Online Mode (connects to DB via asyncpg) ---------------------------------
def run_migrations_online() -> None:
    """Run migrations in 'online' mode -- connects to the database."""
    asyncio.run(_run_async_migrations())


async def _run_async_migrations() -> None:
    """
    Build the async engine DIRECTLY from settings.DATABASE_URL.

    NOTE: We do NOT use async_engine_from_config() here because that
    re-reads alembic.ini which has no sqlalchemy.url entry, causing
    a fallback to localhost and a ConnectionRefusedError.
    """
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)

    await connectable.dispose()


def _do_run_migrations(connection) -> None:
    """Configure the migration context and run."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,            # detect column type changes
        compare_server_default=True,  # detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


# -- Entry Point --------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
