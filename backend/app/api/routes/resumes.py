"""Resume upload and status routes."""

import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.resume import Resume
from app.models.enums import PipelineStatus
from app.models.user import User
from app.schemas.resume import ResumeUploadResponse, ResumeStatusResponse

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _validate_file_type(filename: str) -> None:
    import os

    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )


async def _run_pipeline(resume_id: uuid.UUID, job_id: uuid.UUID, file_bytes: bytes, filename: str) -> None:
    """Background task: run the AI pipeline on the uploaded resume."""
    try:
        from app.agents.orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator()
        await orchestrator.run(
            resume_id=str(resume_id),
            job_id=str(job_id),
            file_bytes=file_bytes,
            filename=filename,
        )
    except Exception as e:
        logger.error("Pipeline failed for resume %s: %s", resume_id, e)


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    job_id: uuid.UUID,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    candidate_email: str | None = None,
    candidate_name: str | None = None,
):
    # Validate file type
    _validate_file_type(file.filename or "")

    # Verify job exists
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    if job_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    # Find or create candidate
    candidate = None
    if candidate_email:
        result = await db.execute(select(Candidate).where(Candidate.email == candidate_email))
        candidate = result.scalar_one_or_none()
    if candidate is None:
        candidate = Candidate(name=candidate_name, email=candidate_email)
        db.add(candidate)
        await db.flush()

    # Read file bytes
    file_bytes = await file.read()

    # Upload to Supabase Storage (best-effort)
    file_path = f"resumes/{candidate.id}/{file.filename}"
    try:
        from app.db.supabase_client import get_supabase

        sb = get_supabase()
        sb.storage.from_("resumes").upload(file_path, file_bytes)
    except Exception as e:
        logger.warning("Supabase storage upload failed: %s", e)
        # Continue — file_path is still set as the intended path

    # Create resume record
    resume = Resume(
        candidate_id=candidate.id,
        job_id=job_id,
        file_path=file_path,
        pipeline_status=PipelineStatus.uploaded,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    # Trigger pipeline in background
    background_tasks.add_task(_run_pipeline, resume.id, job_id, file_bytes, file.filename or "resume")

    return resume


@router.get("/{resume_id}/status", response_model=ResumeStatusResponse)
async def get_resume_status(
    resume_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume
