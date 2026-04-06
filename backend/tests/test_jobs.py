"""Job CRUD tests."""

import pytest
from httpx import AsyncClient

from tests.conftest import register_and_login


@pytest.mark.asyncio
async def test_create_job(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/jobs", json={
        "title": "Backend Engineer",
        "description": "Build APIs with FastAPI.",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Backend Engineer"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_list_jobs(client: AsyncClient, auth_headers: dict):
    await client.post("/api/jobs", json={
        "title": "Job 1",
        "description": "Desc 1",
    }, headers=auth_headers)
    await client.post("/api/jobs", json={
        "title": "Job 2",
        "description": "Desc 2",
    }, headers=auth_headers)

    resp = await client.get("/api/jobs", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["jobs"]) == 2


@pytest.mark.asyncio
async def test_get_job_by_id(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/api/jobs", json={
        "title": "Find Me",
        "description": "Can you find this job?",
    }, headers=auth_headers)
    job_id = create_resp.json()["id"]

    resp = await client.get(f"/api/jobs/{job_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Find Me"


@pytest.mark.asyncio
async def test_get_job_not_found(client: AsyncClient, auth_headers: dict):
    import uuid
    resp = await client.get(f"/api/jobs/{uuid.uuid4()}", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_job(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/api/jobs", json={
        "title": "Old Title",
        "description": "Old desc",
    }, headers=auth_headers)
    job_id = create_resp.json()["id"]

    resp = await client.put(f"/api/jobs/{job_id}", json={
        "title": "New Title",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Title"


@pytest.mark.asyncio
async def test_update_job_not_owner(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/api/jobs", json={
        "title": "Owner Only",
        "description": "Only owner can edit",
    }, headers=auth_headers)
    job_id = create_resp.json()["id"]

    other_headers = await register_and_login(client, email="other@example.com")
    resp = await client.put(f"/api/jobs/{job_id}", json={
        "title": "Hacked",
    }, headers=other_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_job_invalid_data(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/jobs", json={
        "title": "",
        "description": "",
    }, headers=auth_headers)
    assert resp.status_code == 422
