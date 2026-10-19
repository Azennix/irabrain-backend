from abc import ABC, abstractmethod

from .project_decision import ProjectDecision


class ProjectDecisionRepository(ABC):

    @abstractmethod
    def create(self, decision: ProjectDecision) -> ProjectDecision:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(
        self,
        decision_id: str,
        user_id: int,
    ) -> ProjectDecision | None:
        raise NotImplementedError

    @abstractmethod
    def get_all(
        self,
        project_id: str,
        user_id: int,
    ) -> list[ProjectDecision]:
        raise NotImplementedError

    @abstractmethod
    def update(self, decision: ProjectDecision) -> ProjectDecision:
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        decision_id: str,
        user_id: int,
    ) -> None:
        raise NotImplementedError