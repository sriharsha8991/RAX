"""Candidate listing routes."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, outerjoin
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.models.enums import PipelineStatus
from app.models.user import User
from app.schemas.candidate import CandidateResponse, CandidateListResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/jobs/{job_id}/candidates", response_model=CandidateListResponse)
async def list_candidates_for_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    min_score: float | None = Query(None, ge=0, le=100),
):
    # Verify current user owns the job
    job_check = await db.execute(
        select(Job.id).where(Job.id == job_id, Job.created_by == current_user.id)
    )
    if job_check.scalar_one_or_none() is None:
        logger.warning("Candidates list — job %s not found for user %s", job_id, current_user.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    # Join candidates → resumes → analyses for the given job
    stmt = (
        select(
            Candidate,
            Resume.id.label("resume_id"),
            Resume.pipeline_status,
            Analysis.overall_score,
            Analysis.skills_score,
            Analysis.experience_score,
            Analysis.education_score,
            Analysis.explanation,
        )
        .select_from(Candidate)
        .join(Resume, Resume.candidate_id == Candidate.id)
        .outerjoin(Analysis, Analysis.resume_id == Resume.id)
        .where(Resume.job_id == job_id)
    )

    if min_score is not None:
        stmt = stmt.where(Analysis.overall_score >= min_score)

    stmt = stmt.order_by(Analysis.overall_score.desc().nullslast())

    result = await db.execute(stmt)
    rows = result.all()

    candidates = []
    for candidate, resume_id, pipeline_status, overall_score, skills_score, experience_score, education_score, explanation in rows:
        candidates.append(
            CandidateResponse(
                id=candidate.id,
                name=candidate.name,
                email=candidate.email,
                phone=candidate.phone,
                resume_id=resume_id,
                overall_score=overall_score,
                skills_score=skills_score,
                experience_score=experience_score,
                education_score=education_score,
                explanation=explanation,
                pipeline_status=pipeline_status.value if pipeline_status else None,
                created_at=candidate.created_at,
            )
        )
    return CandidateListResponse(candidates=candidates, total=len(candidates))
