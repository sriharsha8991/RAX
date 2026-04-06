import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    overall_score: float | None = None
    pipeline_status: str | None = None
    created_at: datetime


class CandidateListResponse(BaseModel):
    candidates: list[CandidateResponse]
    total: int
