from abc import ABC, abstractmethod

from database.models import ProjectEntity

from .project_model import Project


class ProjectRepository(ABC):

    @abstractmethod
    def create(self, project: Project) -> Project:
        pass

    @abstractmethod
    def get_by_id(
        self,
        project_id: str,
        user_id: int,
    ) -> Project | None:
        pass

    @abstractmethod
    def get_all(
        self,
        user_id: int,
    ) -> list[Project]:
        pass

    @abstractmethod
    def update(self, project: Project) -> Project:
        pass

    @abstractmethod
    def delete(
        self,
        project_id: str,
        user_id: int,
    ) -> bool:
        pass