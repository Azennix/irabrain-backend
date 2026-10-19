from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Project:
    project_id: str
    user_id: int
    name: str
    description: str | None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None