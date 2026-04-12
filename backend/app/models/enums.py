import enum


class UserRole(str, enum.Enum):
    recruiter = "recruiter"
    hiring_manager = "hiring_manager"


class JobStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    closed = "closed"


class PipelineStatus(str, enum.Enum):
    uploaded = "uploaded"
    parsing = "parsing"
    filtering = "filtering"
    ingesting = "ingesting"
    embedding = "embedding"
    matching = "matching"
    scoring = "scoring"
    completed = "completed"
    failed = "failed"


class NotificationStatus(str, enum.Enum):
    not_sent = "not_sent"
    shortlisted = "shortlisted"
    rejected = "rejected"
