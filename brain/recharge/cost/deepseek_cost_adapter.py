from __future__ import annotations

from decimal import Decimal

from brain.recharge.cost.deepseek_cost_source import DeepSeekCostSource
from brain.recharge.models import BrainUsageContext


class DeepSeekCostAdapter:
    def __init__(self) -> None:
        self._source = DeepSeekCostSource(
            input_cost_per_million=Decimal("0.15"),
            output_cost_per_million=Decimal("0.60"),
            cached_input_cost_per_million=Decimal("0.02"),
        )

    def resolve(self, usage) -> Decimal:
        context = BrainUsageContext(
            request_id=usage.request_id,
            user_id=usage.user_id,
            provider=usage.provider,
            model=usage.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cached_tokens=usage.cached_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            total_tokens=usage.total_tokens,
        )

        cost = self._source.resolve(context)

        if cost is None:
            raise ValueError(
                f"Unable to resolve cost for provider: {usage.provider}"
            )

        return cost.amount