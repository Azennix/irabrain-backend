from abc import ABC, abstractmethod

from .task_model import ProjectTask


class ProjectTaskRepository(ABC):

    @abstractmethod
    def create(
        self,
        task: ProjectTask,
    ) -> ProjectTask:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(
        self,
        task_id: str,
        project_id: str,
        user_id: int,
    ) -> ProjectTask | None:
        raise NotImplementedError

    @abstractmethod
    def get_all(
        self,
        project_id: str,
        user_id: int,
    ) -> list[ProjectTask]:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        task: ProjectTask,
    ) -> ProjectTask:
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        task_id: str,
        project_id: str,
        user_id: int,
    ) -> bool:
        raise NotImplementedError