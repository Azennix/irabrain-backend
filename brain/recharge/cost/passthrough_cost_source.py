from decimal import Decimal

from brain.recharge.cost.cost_result import ExecutionCost
from brain.recharge.cost.cost_source import ExecutionCostSource
from brain.recharge.models import BrainUsageContext


class PassthroughExecutionCostSource(ExecutionCostSource):

    @property
    def name(self) -> str:
        return "passthrough"

    @property
    def version(self) -> str:
        return "v1"

    def resolve(
        self,
        context: BrainUsageContext,
    ) -> ExecutionCost | None:
        if context.estimated_cost is None:
            return None

        cost = Decimal(str(context.estimated_cost))

        if cost < Decimal("0"):
            raise ValueError("Execution cost cannot be negative.")

        currency = str(
            context.metadata.get("cost_currency", "USD")
        )

        return ExecutionCost(
            amount=cost,
            currency=currency,
            source=self.name,
            version=self.version,
            metadata={
                "provider": context.provider,
                "model": context.model,
            },
        )