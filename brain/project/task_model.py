from dataclasses import dataclass


@dataclass(slots=True)
class ProjectTask:
    task_id: str
    project_id: str
    goal_id: str | None
    user_id: int
    title: str
    description: str | None
    status: str