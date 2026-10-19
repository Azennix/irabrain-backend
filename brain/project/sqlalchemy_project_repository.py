from sqlalchemy.orm import Session

from database.models import ProjectEntity

from .project_model import Project
from .project_repository import ProjectRepository


class SQLAlchemyProjectRepository(ProjectRepository):

    def __init__(self, session: Session):
        self.session = session

    def create(self, project: Project) -> Project:
        entity = ProjectEntity(
            project_id=project.project_id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            status=project.status,
        )

        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)

        return self._to_domain(entity)

    def get_by_id(
        self,
        project_id: str,
        user_id: int,
    ) -> Project | None:

        entity = (
            self.session.query(ProjectEntity)
            .filter(
                ProjectEntity.project_id == project_id,
                ProjectEntity.user_id == user_id,
            )
            .first()
        )

        if entity is None:
            return None

        return self._to_domain(entity)

    def get_all(
        self,
        user_id: int,
    ) -> list[Project]:

        entities = (
            self.session.query(ProjectEntity)
            .filter(
                ProjectEntity.user_id == user_id,
            )
            .order_by(ProjectEntity.name.asc())
            .all()
        )

        return [
            self._to_domain(entity)
            for entity in entities
        ]

    def update(self, project: Project) -> Project:

        entity = (
            self.session.query(ProjectEntity)
            .filter(
                ProjectEntity.project_id == project.project_id,
                ProjectEntity.user_id == project.user_id,
            )
            .first()
        )

        if entity is None:
            raise ValueError("Project not found.")

        entity.name = project.name
        entity.description = project.description
        entity.status = project.status

        self.session.commit()
        self.session.refresh(entity)

        return self._to_domain(entity)

    def delete(
        self,
        project_id: str,
        user_id: int,
    ) -> bool:

        entity = (
            self.session.query(ProjectEntity)
            .filter(
                ProjectEntity.project_id == project_id,
                ProjectEntity.user_id == user_id,
            )
            .first()
        )

        if entity is None:
            return False

        self.session.delete(entity)
        self.session.commit()

        return True

    @staticmethod
    def _to_domain(entity: ProjectEntity) -> Project:

        return Project(
            project_id=entity.project_id,
            user_id=entity.user_id,
            name=entity.name,
            description=entity.description,
            status=entity.status,
        )