"""Auth endpoint tests: register, login, token, role guard."""

import pytest
from httpx import AsyncClient

from tests.conftest import register_and_login


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post("/api/auth/register", json={
        "email": "new@example.com",
        "password": "securepass1",
        "full_name": "New User",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert data["full_name"] == "New User"
    assert data["role"] == "recruiter"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "password": "securepass1",
        "full_name": "First",
    })
    resp = await client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "password": "securepass2",
        "full_name": "Second",
    })
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "login@example.com",
        "password": "securepass1",
        "full_name": "Login User",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "securepass1",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "wrong@example.com",
        "password": "securepass1",
        "full_name": "Wrong Pass",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "badpassword",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient):
    resp = await client.post("/api/auth/login", json={
        "email": "ghost@example.com",
        "password": "whatever",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    resp = await client.get("/api/jobs")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_invalid_token(client: AsyncClient):
    resp = await client.get("/api/jobs", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_role_guard_forbidden(client: AsyncClient):
    """Hiring managers should not be able to generate feedback (recruiter-only)."""
    headers = await register_and_login(client, email="hm@example.com", role="hiring_manager")
    # POST /feedback requires recruiter role
    import uuid
    resp = await client.post(
        f"/api/feedback/{uuid.uuid4()}/{uuid.uuid4()}",
        headers=headers,
    )
    assert resp.status_code == 403
