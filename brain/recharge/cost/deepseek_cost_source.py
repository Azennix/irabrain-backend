from __future__ import annotations

from decimal import Decimal

from brain.recharge.models import BrainUsageContext
from brain.recharge.cost.cost_result import ExecutionCost
from brain.recharge.cost.cost_source import ExecutionCostSource


class DeepSeekCostSource(ExecutionCostSource):
    """
    Resolves the technical execution cost of DeepSeek API usage.

    Prices are configuration, not product pricing.
    Brain Recharge pricing is handled separately.
    """

    def __init__(
        self,
        input_cost_per_million: Decimal,
        output_cost_per_million: Decimal,
        cached_input_cost_per_million: Decimal | None = None,
        version: str = "deepseek-v4.1-flash-1",
    ):
        self._input_cost_per_million = input_cost_per_million
        self._output_cost_per_million = output_cost_per_million
        self._cached_input_cost_per_million = (
            cached_input_cost_per_million
        )
        self._version = version

    @property
    def name(self) -> str:
        return "deepseek"

    @property
    def version(self) -> str:
        return self._version

    def resolve(
        self,
        context: BrainUsageContext,
    ) -> ExecutionCost | None:
        if context is None:
            raise ValueError(
                "Brain usage context is required."
            )

        if context.provider != "deepseek":
            return None

        input_tokens = context.input_tokens or 0
        output_tokens = context.output_tokens or 0
        cached_tokens = context.cached_tokens or 0

        if input_tokens < 0:
            raise ValueError(
                "Input tokens cannot be negative."
            )

        if output_tokens < 0:
            raise ValueError(
                "Output tokens cannot be negative."
            )

        if cached_tokens < 0:
            raise ValueError(
                "Cached tokens cannot be negative."
            )

        regular_input_tokens = max(
            input_tokens - cached_tokens,
            0,
        )

        input_cost = (
            Decimal(regular_input_tokens)
            / Decimal("1000000")
        ) * self._input_cost_per_million

        if self._cached_input_cost_per_million is not None:
            cached_cost = (
                Decimal(cached_tokens)
                / Decimal("1000000")
            ) * self._cached_input_cost_per_million
        else:
            cached_cost = Decimal("0")

        output_cost = (
            Decimal(output_tokens)
            / Decimal("1000000")
        ) * self._output_cost_per_million

        total_cost = input_cost + cached_cost + output_cost

        return ExecutionCost(
            amount=total_cost,
            currency="USD",
            source=self.name,
            version=self.version,
            metadata={
                "provider": context.provider,
                "model": context.model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cached_tokens": cached_tokens,
            },
        )