"""Feedback generation and retrieval routes."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.candidate import Candidate
from app.models.feedback import Feedback
from app.models.resume import Resume
from app.models.user import User
from app.schemas.feedback import FeedbackResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{candidate_id}/{job_id}", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def generate_feedback(
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("recruiter")),
):
    # Find the resume for this candidate/job pair
    result = await db.execute(
        select(Resume).where(Resume.candidate_id == candidate_id, Resume.job_id == job_id)
    )
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found for this candidate/job")

    # Find the analysis
    analysis_result = await db.execute(select(Analysis).where(Analysis.resume_id == resume.id))
    analysis = analysis_result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found — pipeline not complete")

    # Generate feedback via FeedbackAgent (best-effort)
    feedback_content = "Automated feedback generation pending."
    try:
        from app.agents.feedback_agent import FeedbackAgent
        from app.agents.pipeline_context import PipelineContext

        ctx = PipelineContext(
            resume_id=str(resume.id),
            job_id=str(job_id),
        )
        ctx.analysis = {
            "overall_score": analysis.overall_score,
            "skills_score": analysis.skills_score,
            "experience_score": analysis.experience_score,
            "education_score": analysis.education_score,
            "strengths": analysis.strengths,
            "gaps": analysis.gaps,
            "explanation": analysis.explanation,
        }
        agent = FeedbackAgent()
        await agent.run(ctx)
        feedback_content = ctx.analysis.get("feedback", feedback_content)
    except Exception as e:
        logger.warning("FeedbackAgent failed for candidate %s / job %s: %s", candidate_id, job_id, e)

    feedback = Feedback(
        candidate_id=candidate_id,
        job_id=job_id,
        resume_id=resume.id,
        content=feedback_content,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
    feedback = result.scalar_one_or_none()
    if feedback is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    return feedback
