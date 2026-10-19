
from abc import ABC, abstractmethod

from brain.ai.intent.intent_result import IntentResult


class IntentClassifier(ABC):

    @abstractmethod
    def classify(
        self,
        text: str
    ) -> IntentResult:
        pass