from dataclasses import dataclass


@dataclass(slots=True)
class ProjectContext:
    project_id: str
    project_name: str
    project_description: str | None
    project_status: str

    goals: list[dict]
    tasks: list[dict]
    decisions: list[dict]