from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ProjectDecision:
    decision_id: str
    project_id: str
    user_id: int
    title: str
    description: str | None
    reason: str | None
    status: str
    created_at: datetime
    updated_at: datetime