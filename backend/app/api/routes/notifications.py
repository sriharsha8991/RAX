"""Candidate email notification routes."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.models.job import Job
from app.models.user import User
from app.models.enums import NotificationStatus
from app.services.email_service import (
    send_email,
    build_shortlisted_email,
    build_rejected_email,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class NotifyRequest(BaseModel):
    type: str  # "shortlisted" | "rejected"
    custom_message: str | None = None


class NotifyResponse(BaseModel):
    status: str
    message: str
    email_sent_to: str


@router.post(
    "/candidates/{candidate_id}/notify",
    response_model=NotifyResponse,
)
async def notify_candidate(
    candidate_id: uuid.UUID,
    body: NotifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a shortlisted or rejected email notification to a candidate."""
    if body.type not in ("shortlisted", "rejected"):
        raise HTTPException(status_code=400, detail="type must be 'shortlisted' or 'rejected'")

    # Load candidate
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if not candidate.email:
        raise HTTPException(status_code=400, detail="Candidate has no email address on file")

    # Find the resume + analysis for this candidate (most recent)
    resume_result = await db.execute(
        select(Resume)
        .where(Resume.candidate_id == candidate_id)
        .order_by(Resume.created_at.desc())
        .limit(1)
    )
    resume = resume_result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=404, detail="No resume found for this candidate")

    # Verify current user owns the job
    job_result = await db.execute(
        select(Job).where(Job.id == resume.job_id, Job.created_by == current_user.id)
    )
    job = job_result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=403, detail="You do not have permission to notify this candidate")

    # Load analysis for feedback data
    analysis_result = await db.execute(
        select(Analysis).where(Analysis.resume_id == resume.id)
    )
    analysis = analysis_result.scalar_one_or_none()

    # Build email
    if body.type == "shortlisted":
        subject, html = build_shortlisted_email(
            candidate_name=candidate.name or "",
            job_title=job.title,
            custom_message=body.custom_message,
        )
    else:
        subject, html = build_rejected_email(
            candidate_name=candidate.name or "",
            job_title=job.title,
            gaps=analysis.gaps if analysis else None,
            strengths=analysis.strengths if analysis else None,
            custom_message=body.custom_message,
        )

    # Send email
    try:
        await send_email(to=candidate.email, subject=subject, html_body=html)
    except RuntimeError as e:
        logger.error("Email failed for candidate %s: %s", candidate_id, e)
        raise HTTPException(status_code=502, detail=str(e))

    # Update notification status
    new_status = (
        NotificationStatus.shortlisted
        if body.type == "shortlisted"
        else NotificationStatus.rejected
    )
    candidate.notification_status = new_status
    await db.commit()

    logger.info(
        "Notification sent: candidate=%s type=%s email=%s job=%s",
        candidate_id, body.type, candidate.email, job.title,
    )

    return NotifyResponse(
        status="sent",
        message=f"{'Shortlisted' if body.type == 'shortlisted' else 'Rejection'} email sent successfully",
        email_sent_to=candidate.email,
    )
