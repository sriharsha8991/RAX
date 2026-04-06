import uuid
from datetime import datetime

from sqlalchemy import String, Text, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import JobStatus


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements_raw: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    embedding_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus, name="jobstatus"), nullable=False, default=JobStatus.active)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # relationships
    creator = relationship("User", back_populates="jobs", lazy="selectin")
    resumes = relationship("Resume", back_populates="job", lazy="selectin")
