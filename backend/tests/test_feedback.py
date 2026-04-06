"""Feedback generation and retrieval tests."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.models.feedback import Feedback
from app.models.enums import PipelineStatus
from tests.conftest import register_and_login


@pytest.mark.asyncio
async def test_generate_feedback(client: AsyncClient, auth_headers: dict, sample_job: dict, db_session: AsyncSession):
    job_id = uuid.UUID(sample_job["id"])

    candidate = Candidate(name="Test", email="fb@example.com")
    db_session.add(candidate)
    await db_session.flush()

    resume = Resume(candidate_id=candidate.id, job_id=job_id, file_path="resumes/test.pdf", pipeline_status=PipelineStatus.completed)
    db_session.add(resume)
    await db_session.flush()

    analysis = Analysis(resume_id=resume.id, job_id=job_id, overall_score=85.0, explanation="Good fit")
    db_session.add(analysis)
    await db_session.commit()

    resp = await client.post(
        f"/api/feedback/{candidate.id}/{job_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["candidate_id"] == str(candidate.id)
    assert data["job_id"] == str(job_id)
    assert "content" in data


@pytest.mark.asyncio
async def test_get_feedback(client: AsyncClient, auth_headers: dict, sample_job: dict, db_session: AsyncSession):
    job_id = uuid.UUID(sample_job["id"])

    candidate = Candidate(name="Get FB", email="getfb@example.com")
    db_session.add(candidate)
    await db_session.flush()

    resume = Resume(candidate_id=candidate.id, job_id=job_id, file_path="resumes/getfb.pdf", pipeline_status=PipelineStatus.completed)
    db_session.add(resume)
    await db_session.flush()

    feedback = Feedback(candidate_id=candidate.id, job_id=job_id, resume_id=resume.id, content="Great candidate!")
    db_session.add(feedback)
    await db_session.commit()

    resp = await client.get(f"/api/feedback/{feedback.id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["content"] == "Great candidate!"


@pytest.mark.asyncio
async def test_get_feedback_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.get(f"/api/feedback/{uuid.uuid4()}", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_generate_feedback_no_resume(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        f"/api/feedback/{uuid.uuid4()}/{uuid.uuid4()}",
        headers=auth_headers,
    )
    assert resp.status_code == 404
