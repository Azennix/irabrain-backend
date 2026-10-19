from abc import ABC, abstractmethod


class BaseAIService(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str
    ):
        pass