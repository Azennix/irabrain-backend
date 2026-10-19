from brain.recharge.models import BrainUsageContext
from brain.recharge.settlement import BrainUsageSettlementService
from brain.recharge.calculator import BrainUnitCalculator
from brain.llm.usage import LLMUsageRecord


class LLMUsageToBrainUsageAdapter:
    def __init__(
        self,
        settlement_service: BrainUsageSettlementService,
        unit_calculator: BrainUnitCalculator,
    ):
        if settlement_service is None:
            raise ValueError("Settlement service is required.")

        if unit_calculator is None:
            raise ValueError("Brain Unit calculator is required.")

        self._settlement_service = settlement_service
        self._unit_calculator = unit_calculator

    def settle(
        self,
        usage: LLMUsageRecord,
    ):
        if usage is None:
            raise ValueError("LLM usage record is required.")

        if usage.user_id is None:
            raise ValueError(
                "User ID is required for Brain Unit settlement."
            )

        context = BrainUsageContext(
            request_id=usage.request_id,
            user_id=int(usage.user_id),
            brain_tier=usage.brain_tier,
            provider=usage.provider,
            model=usage.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cached_tokens=usage.cached_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            total_tokens=usage.total_tokens,
            estimated_cost=usage.estimated_cost,
            metadata={
                "source": "llm_usage",
            },
        )

        return self._settlement_service.settle(
            context=context,
            unit_calculator=self._unit_calculator,
        )