import uuid

from .goal_model import Goal
from .goal_repository import GoalRepository


class GoalService:

    def __init__(self, repository: GoalRepository):
        self.repository = repository

    def create_goal(
        self,
        user_id: int,
        project_id: str,
        title: str,
        description: str | None = None,
    ) -> Goal:

        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError("Goal title is required.")

        goal = Goal(
            goal_id=str(uuid.uuid4()),
            project_id=project_id,
            user_id=user_id,
            title=normalized_title,
            description=description.strip() if description else None,
            status="active",
        )

        return self.repository.create(goal)

    def get_goal(
        self,
        user_id: int,
        project_id: str,
        goal_id: str,
    ) -> Goal | None:

        return self.repository.get_by_id(
            goal_id=goal_id,
            project_id=project_id,
            user_id=user_id,
        )

    def get_goals(
        self,
        user_id: int,
        project_id: str,
    ) -> list[Goal]:

        return self.repository.get_all(
            project_id=project_id,
            user_id=user_id,
        )

    def update_goal(
        self,
        user_id: int,
        project_id: str,
        goal_id: str,
        title: str,
        description: str | None,
        status: str,
    ) -> Goal:

        goal = self.repository.get_by_id(
            goal_id=goal_id,
            project_id=project_id,
            user_id=user_id,
        )

        if goal is None:
            raise ValueError("Goal not found.")

        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError("Goal title is required.")

        goal.title = normalized_title
        goal.description = description.strip() if description else None
        goal.status = status

        return self.repository.update(goal)

    def delete_goal(
        self,
        user_id: int,
        project_id: str,
        goal_id: str,
    ) -> bool:

        return self.repository.delete(
            goal_id=goal_id,
            project_id=project_id,
            user_id=user_id,
        )