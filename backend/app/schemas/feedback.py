import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    resume_id: uuid.UUID
    content: str
    sent_at: datetime | None = None
    created_at: datetime
