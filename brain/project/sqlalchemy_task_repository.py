from sqlalchemy.orm import Session

from database.models import ProjectTaskEntity

from .task_model import ProjectTask
from .task_repository import ProjectTaskRepository


class SQLAlchemyProjectTaskRepository(
    ProjectTaskRepository
):

    def __init__(self, session: Session):
        self.session = session

    def _to_domain(
        self,
        entity: ProjectTaskEntity,
    ) -> ProjectTask:
        return ProjectTask(
            task_id=entity.task_id,
            project_id=entity.project_id,
            goal_id=entity.goal_id,
            user_id=entity.user_id,
            title=entity.title,
            description=entity.description,
            status=entity.status,
        )

    def create(
        self,
        task: ProjectTask,
    ) -> ProjectTask:
        entity = ProjectTaskEntity(
            task_id=task.task_id,
            project_id=task.project_id,
            goal_id=task.goal_id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status,
        )

        self.session.add(entity)
        self.session.flush()
        self.session.commit()

        return self._to_domain(entity)

    def get_by_id(
        self,
        task_id: str,
        project_id: str,
        user_id: int,
    ) -> ProjectTask | None:
        entity = (
            self.session.query(ProjectTaskEntity)
            .filter(
                ProjectTaskEntity.task_id == task_id,
                ProjectTaskEntity.project_id == project_id,
                ProjectTaskEntity.user_id == user_id,
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
    ) -> list[ProjectTask]:
        entities = (
            self.session.query(ProjectTaskEntity)
            .filter(
                ProjectTaskEntity.project_id == project_id,
                ProjectTaskEntity.user_id == user_id,
            )
            .all()
        )

        return [
            self._to_domain(entity)
            for entity in entities
        ]

    def update(
        self,
        task: ProjectTask,
    ) -> ProjectTask:
        entity = (
            self.session.query(ProjectTaskEntity)
            .filter(
                ProjectTaskEntity.task_id == task.task_id,
                ProjectTaskEntity.project_id == task.project_id,
                ProjectTaskEntity.user_id == task.user_id,
            )
            .first()
        )

        if entity is None:
            raise ValueError("Task not found")

        entity.title = task.title
        entity.description = task.description
        entity.goal_id = task.goal_id
        entity.status = task.status

        self.session.flush()
        self.session.commit()

        return self._to_domain(entity)

    def delete(
        self,
        task_id: str,
        project_id: str,
        user_id: int,
    ) -> bool:
        entity = (
            self.session.query(ProjectTaskEntity)
            .filter(
                ProjectTaskEntity.task_id == task_id,
                ProjectTaskEntity.project_id == project_id,
                ProjectTaskEntity.user_id == user_id,
            )
            .first()
        )

        if entity is None:
            return False

        self.session.delete(entity)
        self.session.flush()
        self.session.commit()

        return True