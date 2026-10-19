from abc import ABC, abstractmethod

from brain.base.brain_request import BrainRequest
from brain.memory.memory_intent_result import MemoryIntentResult


class IntentRule(ABC):

    @abstractmethod
    def execute(
        self,
        request: BrainRequest
    ) -> MemoryIntentResult:
        pass