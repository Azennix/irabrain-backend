from abc import ABC, abstractmethod

from brain.recharge.models import BrainUsageContext
from brain.recharge.cost.cost_result import ExecutionCost


class ExecutionCostSource(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def resolve(
        self,
        context: BrainUsageContext,
    ) -> ExecutionCost | None:
        raise NotImplementedError