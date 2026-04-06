"""Async SQLAlchemy engine and session factory."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

# Supabase requires sslmode=require; asyncpg uses the 'ssl' query-param instead
_url = settings.DATABASE_URL
if _url.startswith("postgresql://"):
    _url = _url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _url.startswith("postgres://"):
    _url = _url.replace("postgres://", "postgresql+asyncpg://", 1)

async_engine = create_async_engine(_url, echo=False, pool_pre_ping=True)

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
