"""Shared test fixtures: in-memory SQLite DB, async client, auth helpers."""

import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.models import User, Job, Candidate, Resume, Analysis, Feedback  # noqa: F401  — ensure all models registered
from app.models.enums import UserRole

# ── Map PostgreSQL JSONB → SQLite JSON for testing ──
from sqlalchemy import JSON
from sqlalchemy.ext.compiler import compiles

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

# ── In-memory SQLite engine (async via aiosqlite) ──
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionFactory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Use a single event loop for all tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture
async def client():
    """Async HTTP client pointing at the test app with overridden DB."""
    from app.main import app

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Raw DB session for direct queries in tests."""
    async with TestSessionFactory() as session:
        yield session


# ── Auth helpers ──

async def register_and_login(client: AsyncClient, email: str = "test@example.com", password: str = "testpass123", role: str = "recruiter") -> dict:
    """Register a user and return auth headers."""
    await client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test User",
        "role": role,
    })
    resp = await client.post("/api/auth/login", json={
        "email": email,
        "password": password,
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict:
    """Auth headers for a default recruiter user."""
    return await register_and_login(client)


@pytest_asyncio.fixture
async def recruiter_headers(client: AsyncClient) -> dict:
    """Auth headers for a recruiter."""
    return await register_and_login(client, email="recruiter@example.com", role="recruiter")


@pytest_asyncio.fixture
async def sample_job(client: AsyncClient, auth_headers: dict) -> dict:
    """Create and return a sample job."""
    resp = await client.post("/api/jobs", json={
        "title": "Senior Python Developer",
        "description": "We need a senior Python dev with FastAPI experience.",
        "requirements_raw": {"skills": ["python", "fastapi", "postgresql"]},
    }, headers=auth_headers)
    return resp.json()
