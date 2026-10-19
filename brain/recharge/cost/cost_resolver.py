from brain.recharge.cost.cost_result import ExecutionCost
from brain.recharge.cost.cost_source import ExecutionCostSource
from brain.recharge.models import BrainUsageContext


class ExecutionCostResolver:
    def __init__(self, sources: list[ExecutionCostSource]):
        if not sources:
            raise ValueError("At least one execution cost source is required.")

        self._sources = tuple(sources)

    def resolve(
        self,
        context: BrainUsageContext,
    ) -> ExecutionCost:
        if context is None:
            raise ValueError("Brain usage context is required.")

        for source in self._sources:
            cost = source.resolve(context)

            if cost is not None:
                return cost

        raise ValueError(
            "No execution cost source could resolve the technical execution cost."
        )