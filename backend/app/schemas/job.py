import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    requirements_raw: dict[str, Any] | None = None


class JobUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)
    requirements_raw: dict[str, Any] | None = None
    status: str | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    requirements_raw: dict[str, Any] | None = None
    embedding_id: str | None = None
    created_by: uuid.UUID
    status: str
    created_at: datetime


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
