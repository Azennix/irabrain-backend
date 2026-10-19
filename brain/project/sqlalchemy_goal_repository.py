from sqlalchemy.orm import Session

from database.models import GoalEntity

from .goal_model import Goal
from .goal_repository import GoalRepository


class SQLAlchemyGoalRepository(GoalRepository):

    def __init__(self, session: Session):
        self.session = session

    def create(self, goal: Goal) -> Goal:
        entity = GoalEntity(
            goal_id=goal.goal_id,
            project_id=goal.project_id,
            user_id=goal.user_id,
            title=goal.title,
            description=goal.description,
            status=goal.status,
        )

        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)

        return self._to_domain(entity)

    def get_by_id(
        self,
        goal_id: str,
        project_id: str,
        user_id: int,
    ) -> Goal | None:

        entity = (
            self.session.query(GoalEntity)
            .filter(
                GoalEntity.goal_id == goal_id,
                GoalEntity.project_id == project_id,
                GoalEntity.user_id == user_id,
            )
            .first()
        )

        if entity is None:
            return None

        return self._to_domain(entity)

    def get_all(
        self,
        project_id: str,
        user_id: int,
    ) -> list[Goal]:

        entities = (
            self.session.query(GoalEntity)
            .filter(
                GoalEntity.project_id == project_id,
                GoalEntity.user_id == user_id,
            )
            .order_by(GoalEntity.title.asc())
            .all()
        )

        return [self._to_domain(entity) for entity in entities]

    def update(self, goal: Goal) -> Goal:

        entity = (
            self.session.query(GoalEntity)
            .filter(
                GoalEntity.goal_id == goal.goal_id,
                GoalEntity.project_id == goal.project_id,
                GoalEntity.user_id == goal.user_id,
            )
            .first()
        )

        if entity is None:
            raise ValueError("Goal not found.")

        entity.title = goal.title
        entity.description = goal.description
        entity.status = goal.status

        self.session.commit()
        self.session.refresh(entity)

        return self._to_domain(entity)

    def delete(
        self,
        goal_id: str,
        project_id: str,
        user_id: int,
    ) -> bool:

        entity = (
            self.session.query(GoalEntity)
            .filter(
                GoalEntity.goal_id == goal_id,
                GoalEntity.project_id == project_id,
                GoalEntity.user_id == user_id,
            )
            .first()
        )

        if entity is None:
            return False

        self.session.delete(entity)
        self.session.commit()

        return True

    @staticmethod
    def _to_domain(entity: GoalEntity) -> Goal:
        return Goal(
            goal_id=entity.goal_id,
            project_id=entity.project_id,
            user_id=entity.user_id,
            title=entity.title,
            description=entity.description,
            status=entity.status,
        )