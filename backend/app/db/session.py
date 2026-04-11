"""Async SQLAlchemy engine and session factory."""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Supabase requires sslmode=require; asyncpg uses the 'ssl' query-param instead
_url = settings.DATABASE_URL
if _url.startswith("postgresql://"):
    _url = _url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _url.startswith("postgres://"):
    _url = _url.replace("postgres://", "postgresql+asyncpg://", 1)

# When using SQLite (local dev), map PostgreSQL JSONB → JSON
if "sqlite" in _url:
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy import JSON
    from sqlalchemy.ext.compiler import compiles

    @compiles(JSONB, "sqlite")
    def compile_jsonb_sqlite(type_, compiler, **kw):
        return "JSON"

# Engine kwargs differ between SQLite (tests/dev) and PostgreSQL (production)
_engine_kwargs: dict = {"echo": False, "pool_pre_ping": True}
if "sqlite" not in _url:
    _engine_kwargs.update({"pool_size": 10, "max_overflow": 20})

async_engine = create_async_engine(_url, **_engine_kwargs)
logger.info("SQLAlchemy engine created — %s", "sqlite" if "sqlite" in _url else "postgresql")

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async DB session, auto-closes."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def close_db_engine() -> None:
    """Dispose the engine on shutdown."""
    await async_engine.dispose()
    logger.info("SQLAlchemy engine disposed")
