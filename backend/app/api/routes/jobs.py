"""Job CRUD routes."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=JobListResponse)
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Job).where(Job.created_by == current_user.id).order_by(Job.created_at.desc())
    )
    jobs = list(result.scalars().all())
    logger.info("Listed %d jobs for user %s", len(jobs), current_user.id)
    return JobListResponse(jobs=jobs, total=len(jobs))


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    body: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("recruiter", "hiring_manager")),
):
    job = Job(
        title=body.title,
        description=body.description,
        requirements_raw=body.requirements_raw,
        created_by=current_user.id,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    logger.info("Job created: %s '%s' by user %s", job.id, job.title, current_user.id)

    # Non-blocking agent integration (best-effort)
    try:
        from app.db.neo4j_client import get_neo4j_driver
        from app.agents.graph_ingestion_agent import GraphIngestionAgent

        driver = get_neo4j_driver()
        graph_agent = GraphIngestionAgent(driver=driver)
        await graph_agent.ingest_job(
            job_id=str(job.id),
            title=job.title,
            requirements=job.requirements_raw or {},
        )
    except Exception as e:
        logger.warning("GraphIngestionAgent failed for job %s: %s", job.id, e)

    try:
        from app.agents.embedding_agent import EmbeddingAgent

        embed_agent = EmbeddingAgent()
        embedding_id = await embed_agent.embed_job(
            job_id=str(job.id),
            description_text=job.description,
            title=job.title,
            requirements=job.requirements_raw,
        )
        job.embedding_id = embedding_id
        await db.commit()
    except Exception as e:
        logger.warning("EmbeddingAgent failed for job %s: %s", job.id, e)

    return job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.created_by == current_user.id)
    )
    job = result.scalar_one_or_none()
    if job is None:
        logger.warning("Job %s not found for user %s", job_id, current_user.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: uuid.UUID,
    body: JobUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.created_by != current_user.id:
        logger.warning("Job update denied — user %s not owner of job %s", current_user.id, job_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the job owner")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    await db.commit()
    await db.refresh(job)
    logger.info("Job updated: %s", job_id)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a job and all associated resumes, analyses, and feedback."""
    from app.models.resume import Resume
    from app.models.analysis import Analysis
    from app.models.feedback import Feedback

    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.created_by == current_user.id)
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    # Delete child records: feedback → analysis → resumes → job
    resume_result = await db.execute(select(Resume).where(Resume.job_id == job_id))
    resumes = list(resume_result.scalars().all())
    logger.info("Deleting job %s with %d resumes", job_id, len(resumes))
    for resume in resumes:
        await db.execute(
            select(Feedback).where(Feedback.resume_id == resume.id)
        )
        for fb in resume.feedback_list:
            await db.delete(fb)
        if resume.analysis:
            await db.delete(resume.analysis)
        await db.delete(resume)

    await db.delete(job)
    await db.commit()
