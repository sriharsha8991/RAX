import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    job_id: uuid.UUID
    overall_score: float | None = None
    skills_score: float | None = None
    experience_score: float | None = None
    education_score: float | None = None
    semantic_similarity: float | None = None
    structural_match: float | None = None
    explanation: str | None = None
    strengths: list[Any] | None = None
    gaps: list[Any] | None = None
    graph_paths: list[Any] | None = None
    created_at: datetime
