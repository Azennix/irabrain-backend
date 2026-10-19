from abc import ABC, abstractmethod

from .goal_model import Goal


class GoalRepository(ABC):

    @abstractmethod
    def create(self, goal: Goal) -> Goal:
        pass

    @abstractmethod
    def get_by_id(
        self,
        goal_id: str,
        project_id: str,
        user_id: int,
    ) -> Goal | None:
        pass

    @abstractmethod
    def get_all(
        self,
        project_id: str,
        user_id: int,
    ) -> list[Goal]:
        pass

    @abstractmethod
    def update(self, goal: Goal) -> Goal:
        pass

    @abstractmethod
    def delete(
        self,
        goal_id: str,
        project_id: str,
        user_id: int,
    ) -> bool:
        pass