from dataclasses import dataclass


@dataclass(slots=True)
class Goal:
    goal_id: str
    project_id: str
    user_id: int
    title: str
    description: str | None
    status: str