"""Analysis retrieval routes."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.analysis import AnalysisResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/resumes/{resume_id}/analysis", response_model=AnalysisResponse)
async def get_analysis(
    resume_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Analysis).where(Analysis.resume_id == resume_id))
    analysis = result.scalar_one_or_none()
    if analysis is None:
        logger.warning("Analysis not found for resume %s", resume_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found — pipeline may not be complete",
        )
    logger.info("Analysis retrieved for resume %s — score=%s", resume_id, analysis.overall_score)
    return analysis
