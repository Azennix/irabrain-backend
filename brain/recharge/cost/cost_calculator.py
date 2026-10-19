from decimal import Decimal

from brain.recharge.calculator import BrainUnitCalculator
from brain.recharge.cost.cost_resolver import ExecutionCostResolver
from brain.recharge.models import BrainUsageContext, BrainUnitResult


class CostBasedBrainUnitCalculator:
    def __init__(
        self,
        cost_resolver: ExecutionCostResolver,
        unit_cost: Decimal,
        calculation_version: str,
        target_currency: str = "INR",
        usd_to_inr_rate: Decimal = Decimal("90"),
    ):
        if cost_resolver is None:
            raise ValueError("Execution cost resolver is required.")

        if unit_cost <= Decimal("0"):
            raise ValueError("Brain Unit cost must be greater than zero.")

        if not calculation_version.strip():
            raise ValueError("Calculation version is required.")

        self._cost_resolver = cost_resolver
        self._unit_cost = unit_cost
        self._calculation_version = calculation_version

    def calculate(
        self,
        context: BrainUsageContext,
    ) -> BrainUnitResult:
        if context is None:
            raise ValueError("Brain usage context is required.")

        execution_cost = self._cost_resolver.resolve(context)

        cost_context = BrainUsageContext(
            request_id=context.request_id,
            user_id=context.user_id,
            capability=context.capability,
            task_type=context.task_type,
            provider=context.provider,
            model=context.model,
            input_tokens=context.input_tokens,
            output_tokens=context.output_tokens,
            cached_tokens=context.cached_tokens,
            reasoning_tokens=context.reasoning_tokens,
            total_tokens=context.total_tokens,
            estimated_cost=float(execution_cost.amount),
            tool_usage=context.tool_usage,
            metadata={
                **context.metadata,
                "cost_source": execution_cost.source,
                "cost_version": execution_cost.version,
                "cost_currency": execution_cost.currency,
            },
        )

        calculator = BrainUnitCalculator(
            policy=_CostPolicyAdapter(
                unit_cost=self._unit_cost,
                version=self._calculation_version,
            )
        )

        return calculator.calculate(cost_context)


class _CostPolicyAdapter:
    def __init__(self, unit_cost: Decimal, version: str):
        self._unit_cost = unit_cost
        self._version = version

    @property
    def version(self) -> str:
        return self._version

    def calculate(self, context: BrainUsageContext) -> BrainUnitResult:
        from brain.recharge.calculator import CostBasedBrainUnitPolicy

        policy = CostBasedBrainUnitPolicy(
            unit_cost=self._unit_cost,
            version=self._version,
        )

        return policy.calculate(context)