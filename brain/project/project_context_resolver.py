from .project_context import ProjectContext
from .project_repository import ProjectRepository
from .goal_repository import GoalRepository
from .task_repository import ProjectTaskRepository
from .decision_repository import ProjectDecisionRepository


class ProjectContextResolver:

    def __init__(
        self,
        project_repository: ProjectRepository,
        goal_repository: GoalRepository,
        task_repository: ProjectTaskRepository,
        decision_repository: ProjectDecisionRepository,
    ):
        self.project_repository = project_repository
        self.goal_repository = goal_repository
        self.task_repository = task_repository
        self.decision_repository = decision_repository

    def resolve(
        self,
        project_id: str,
        user_id: int,
    ) -> ProjectContext | None:

        project = self.project_repository.get_by_id(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            return None

        goals = self.goal_repository.get_all(
            project_id=project_id,
            user_id=user_id,
        )

        tasks = self.task_repository.get_all(
            project_id=project_id,
            user_id=user_id,
        )
        decisions = self.decision_repository.get_all(
            project_id=project_id,
            user_id=user_id,
)
        print("PROJECT DECISIONS:", decisions)

        return ProjectContext(
            project_id=project.project_id,
            project_name=project.name,
            project_description=project.description,
            project_status=project.status,
            goals=[
                {
                    "goal_id": goal.goal_id,
                    "title": goal.title,
                    "description": goal.description,
                    "status": goal.status,
                }
                for goal in goals
            ],
            tasks=[
                {
                    "task_id": task.task_id,
                    "goal_id": task.goal_id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                }
                for task in tasks
            ],
            decisions=[
    {
            "decision_id": decision.decision_id,
            "title": decision.title,
            "description": decision.description,
            "reason": decision.reason,
            "status": decision.status,
            "created_at": decision.created_at,
             "updated_at": decision.updated_at,
    }
        for decision in decisions
],
        )