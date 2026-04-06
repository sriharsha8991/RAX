import uuid
from datetime import datetime

from sqlalchemy import String, Text, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PipelineStatus


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    anonymized_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    embedding_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pipeline_status: Mapped[PipelineStatus] = mapped_column(
        Enum(PipelineStatus, name="pipelinestatus"),
        nullable=False,
        default=PipelineStatus.uploaded,
    )
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # relationships
    candidate = relationship("Candidate", back_populates="resumes", lazy="selectin")
    job = relationship("Job", back_populates="resumes", lazy="selectin")
    analysis = relationship("Analysis", back_populates="resume", uselist=False, lazy="selectin")
    feedback_list = relationship("Feedback", back_populates="resume", lazy="selectin")
