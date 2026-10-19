from abc import ABC, abstractmethod

from brain.base.brain_request import BrainRequest
from brain.memory.rule_result import RuleResult


class MemoryRule(ABC):

    """
    Base class for every Memory Rule.
    """

    @abstractmethod
    def execute(
        self,
        request: BrainRequest
    ) -> RuleResult:
        pass