"""Resume upload and status routes."""

import asyncio
import logging
import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.config import get_settings
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

# Track background pipeline tasks so they aren't garbage-collected
_background_tasks: set[asyncio.Task] = set()

# Limit how many pipelines can run concurrently. Extraction itself is now
# very fast (pypdfium2), so the bottleneck is the LLM (Gemini). 6 is a safe
# default that respects typical free-tier rate limits while keeping batches
# of 100 resumes flowing.
_PIPELINE_CONCURRENCY = 6
_pipeline_semaphore: asyncio.Semaphore | None = None


def _get_pipeline_semaphore() -> asyncio.Semaphore:
    global _pipeline_semaphore
    if _pipeline_semaphore is None:
        _pipeline_semaphore = asyncio.Semaphore(_PIPELINE_CONCURRENCY)
    return _pipeline_semaphore


def _sanitize_filename(filename: str) -> str:
    """Strip path-traversal characters and non-safe characters from filename."""
    # Take only the final path component (no ../ tricks)
    import os
    name = os.path.basename(filename)
    # Keep only alphanumeric, dash, underscore, dot
    return re.sub(r"[^\w\-.]", "_", name) or "resume"


def _validate_file_type(filename: str) -> None:
    import os

    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )


async def _run_pipeline(resume_id: uuid.UUID, job_id: uuid.UUID, file_bytes: bytes, filename: str) -> None:
    """Background task: run the AI pipeline on the uploaded resume.

    Guarded by _pipeline_semaphore so that only N pipelines run at once.
    Extra pipelines queue and start as slots free up.
    """
    sem = _get_pipeline_semaphore()
    async with sem:
        await _run_pipeline_inner(resume_id, job_id, file_bytes, filename)


async def _run_pipeline_inner(resume_id: uuid.UUID, job_id: uuid.UUID, file_bytes: bytes, filename: str) -> None:
    """Actual pipeline logic (called under the semaphore)."""
    try:
        from app.agents.orchestrator import PipelineOrchestrator
        from app.api.routes.sse import make_sse_callback
        from app.db.neo4j_client import get_neo4j_driver
        from app.db.qdrant_client import get_qdrant_client
        from app.db.session import async_session_factory
        from app.models.enums import PipelineStatus

        # Get real clients
        try:
            neo4j_driver = get_neo4j_driver()
        except Exception:
            neo4j_driver = None
        try:
            qdrant_client = get_qdrant_client()
        except Exception:
            qdrant_client = None

        sse_callback = make_sse_callback(str(job_id))

        orchestrator = PipelineOrchestrator(
            on_status_change=sse_callback,
            neo4j_driver=neo4j_driver,
            qdrant_client=qdrant_client,
        )
        ctx = await orchestrator.run(
            resume_id=str(resume_id),
            job_id=str(job_id),
            file_bytes=file_bytes,
            filename=filename,
        )

        # Persist analysis results and update pipeline status
        try:
            async with async_session_factory() as db:
                from app.models.resume import Resume
                from app.models.analysis import Analysis
                from app.models.candidate import Candidate
                from sqlalchemy import select

                resume = (await db.execute(select(Resume).where(Resume.id == resume_id))).scalar_one_or_none()
                if resume:
                    # Always persist resume data that was successfully extracted
                    if ctx.raw_text:
                        resume.raw_text = ctx.raw_text
                    if ctx.parsed_resume:
                        resume.parsed_json = ctx.parsed_resume
                        # Update candidate name/email/phone from parsed resume
                        candidate = (await db.execute(
                            select(Candidate).where(Candidate.id == resume.candidate_id)
                        )).scalar_one_or_none()
                        if candidate:
                            parsed_name = ctx.parsed_resume.get("name", "").strip()
                            parsed_email = ctx.parsed_resume.get("email", "").strip()
                            parsed_phone = ctx.parsed_resume.get("phone", "").strip()
                            if parsed_name and not candidate.name:
                                candidate.name = parsed_name
                            if parsed_email and not candidate.email:
                                candidate.email = parsed_email
                            if parsed_phone and not candidate.phone:
                                candidate.phone = parsed_phone
                    if ctx.filtered_resume:
                        resume.anonymized_json = ctx.filtered_resume
                    if ctx.qdrant_point_id:
                        resume.embedding_id = ctx.qdrant_point_id

                    # Create Analysis record if scoring produced results
                    if ctx.analysis:
                        resume.pipeline_status = PipelineStatus.completed
                        analysis = Analysis(
                            resume_id=resume_id,
                            job_id=job_id,
                            overall_score=ctx.analysis.get("overall_score"),
                            skills_score=ctx.analysis.get("skills_score"),
                            experience_score=ctx.analysis.get("experience_score"),
                            education_score=ctx.analysis.get("education_score"),
                            semantic_similarity=ctx.analysis.get("semantic_similarity"),
                            structural_match=ctx.analysis.get("structural_match"),
                            explanation=ctx.analysis.get("explanation"),
                            strengths=ctx.analysis.get("strengths"),
                            gaps=ctx.analysis.get("gaps"),
                            graph_paths=ctx.analysis.get("graph_paths"),
                        )
                        db.add(analysis)
                    elif ctx.error:
                        resume.pipeline_status = PipelineStatus.failed
                    else:
                        resume.pipeline_status = PipelineStatus.failed

                    await db.commit()
        except Exception as persist_err:
            logger.error("Failed to persist pipeline results for resume %s: %s", resume_id, persist_err)
            try:
                await db.rollback()
            except Exception:
                pass

    except Exception as e:
        logger.error("Pipeline failed for resume %s: %s", resume_id, e)


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    job_id: uuid.UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    candidate_email: str | None = None,
    candidate_name: str | None = None,
):
    # Validate file type
    _validate_file_type(file.filename or "")

    # Verify job exists AND current user owns it
    job_result = await db.execute(
        select(Job).where(Job.id == job_id, Job.created_by == current_user.id)
    )
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

    # Read file bytes with size limit
    settings = get_settings()
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    file_bytes = await file.read(max_size + 1)
    if len(file_bytes) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Sanitize filename to prevent path traversal
    safe_filename = _sanitize_filename(file.filename or "resume")

    # Persist file (local FS or Supabase depending on USE_LOCAL_SERVICES)
    file_path = f"resumes/{candidate.id}/{safe_filename}"
    from app.services.storage import save_file
    await save_file(file_bytes, file_path)

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

    # Trigger pipeline as a tracked background task
    task = asyncio.create_task(
        _run_pipeline(resume.id, job_id, file_bytes, file.filename or "resume")
    )
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)

    return resume


@router.post("/upload/batch", response_model=list[ResumeUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_resumes_batch(
    job_id: uuid.UUID,
    files: list[UploadFile],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept multiple files at once.  All DB inserts happen first, then all
    pipelines are kicked off concurrently as background tasks."""

    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided")

    if len(files) > 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum 20 files per batch")

    for f in files:
        _validate_file_type(f.filename or "")

    # Verify job ownership once
    job_result = await db.execute(
        select(Job).where(Job.id == job_id, Job.created_by == current_user.id)
    )
    if job_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    settings = get_settings()
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    results: list[Resume] = []
    pipeline_args: list[tuple[uuid.UUID, uuid.UUID, bytes, str]] = []

    for file in files:
        file_bytes = await file.read(max_size + 1)
        if len(file_bytes) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File '{file.filename}' too large. Maximum: {settings.MAX_UPLOAD_SIZE_MB}MB",
            )

        candidate = Candidate()
        db.add(candidate)
        await db.flush()

        safe_filename = _sanitize_filename(file.filename or "resume")
        file_path = f"resumes/{candidate.id}/{safe_filename}"

        # Persist file (local FS or Supabase depending on USE_LOCAL_SERVICES)
        from app.services.storage import save_file
        await save_file(file_bytes, file_path)

        resume = Resume(
            candidate_id=candidate.id,
            job_id=job_id,
            file_path=file_path,
            pipeline_status=PipelineStatus.uploaded,
        )
        db.add(resume)
        await db.flush()
        pipeline_args.append((resume.id, job_id, file_bytes, file.filename or "resume"))
        results.append(resume)

    await db.commit()
    for r in results:
        await db.refresh(r)

    # Fire all pipelines concurrently — the semaphore in _run_pipeline
    # limits how many actually execute at once.
    for rid, jid, fbytes, fname in pipeline_args:
        task = asyncio.create_task(_run_pipeline(rid, jid, fbytes, fname))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)

    logger.info("Batch upload: %d resumes queued for job %s", len(results), job_id)
    return results


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


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a resume and its associated analysis and feedback records."""
    from app.models.analysis import Analysis
    from app.models.feedback import Feedback

    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    # Verify the current user owns the job this resume belongs to
    job_result = await db.execute(
        select(Job).where(Job.id == resume.job_id, Job.created_by == current_user.id)
    )
    if job_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Delete related analysis and feedback first
    await db.execute(select(Analysis).where(Analysis.resume_id == resume_id))
    if resume.analysis:
        await db.delete(resume.analysis)
    for fb in resume.feedback_list:
        await db.delete(fb)

    await db.delete(resume)
    await db.commit()
