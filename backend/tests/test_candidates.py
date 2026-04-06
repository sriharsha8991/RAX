"""Candidate listing tests."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.models.enums import PipelineStatus


@pytest.mark.asyncio
async def test_list_candidates_empty(client: AsyncClient, auth_headers: dict, sample_job: dict):
    job_id = sample_job["id"]
    resp = await client.get(f"/api/jobs/{job_id}/candidates", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["candidates"] == []


@pytest.mark.asyncio
async def test_list_candidates_sorted_by_score(client: AsyncClient, auth_headers: dict, sample_job: dict, db_session: AsyncSession):
    job_id = uuid.UUID(sample_job["id"])

    # Create two candidates with different scores
    c1 = Candidate(name="Alice", email="alice@example.com")
    c2 = Candidate(name="Bob", email="bob@example.com")
    db_session.add_all([c1, c2])
    await db_session.flush()

    r1 = Resume(candidate_id=c1.id, job_id=job_id, file_path="resumes/alice.pdf", pipeline_status=PipelineStatus.completed)
    r2 = Resume(candidate_id=c2.id, job_id=job_id, file_path="resumes/bob.pdf", pipeline_status=PipelineStatus.completed)
    db_session.add_all([r1, r2])
    await db_session.flush()

    a1 = Analysis(resume_id=r1.id, job_id=job_id, overall_score=75.0)
    a2 = Analysis(resume_id=r2.id, job_id=job_id, overall_score=90.0)
    db_session.add_all([a1, a2])
    await db_session.commit()

    resp = await client.get(f"/api/jobs/{job_id}/candidates", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    # Bob (90) should come before Alice (75)
    assert data["candidates"][0]["name"] == "Bob"
    assert data["candidates"][1]["name"] == "Alice"
