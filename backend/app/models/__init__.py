# Re-export all models so Alembic and other consumers can do:
#   from app.models import User, Job, Candidate, Resume, Analysis, Feedback

from app.models.enums import UserRole, JobStatus, PipelineStatus
from app.models.user import User
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.models.feedback import Feedback

__all__ = [
    "UserRole",
    "JobStatus",
    "PipelineStatus",
    "User",
    "Job",
    "Candidate",
    "Resume",
    "Analysis",
    "Feedback",
]
