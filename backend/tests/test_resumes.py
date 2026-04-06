"""Resume upload and status tests."""

import io
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_resume_pdf(client: AsyncClient, auth_headers: dict, sample_job: dict):
    job_id = sample_job["id"]
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake content")

    resp = await client.post(
        f"/api/resumes/upload?job_id={job_id}",
        files={"file": ("resume.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["pipeline_status"] == "uploaded"
    assert data["job_id"] == job_id


@pytest.mark.asyncio
async def test_upload_resume_invalid_type(client: AsyncClient, auth_headers: dict, sample_job: dict):
    job_id = sample_job["id"]
    fake_txt = io.BytesIO(b"plain text file")

    resp = await client.post(
        f"/api/resumes/upload?job_id={job_id}",
        files={"file": ("resume.txt", fake_txt, "text/plain")},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "invalid file type" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_resume_status(client: AsyncClient, auth_headers: dict, sample_job: dict):
    job_id = sample_job["id"]
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake content")

    upload_resp = await client.post(
        f"/api/resumes/upload?job_id={job_id}",
        files={"file": ("resume.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers,
    )
    resume_id = upload_resp.json()["id"]

    resp = await client.get(f"/api/resumes/{resume_id}/status", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["pipeline_status"] == "uploaded"


@pytest.mark.asyncio
async def test_get_resume_status_not_found(client: AsyncClient, auth_headers: dict):
    import uuid
    resp = await client.get(f"/api/resumes/{uuid.uuid4()}/status", headers=auth_headers)
    assert resp.status_code == 404
