from abc import ABC, abstractmethod

from brain.base.brain_request import BrainRequest


class Engine(ABC):

    """
    Base interface for every IRABRAIN Engine.
    """

    @abstractmethod
    def execute(
        self,
        request: BrainRequest
    ):
        pass