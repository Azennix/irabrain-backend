from decimal import Decimal

from brain.recharge.cost.cost_result import ExecutionCost
from brain.recharge.cost.cost_source import ExecutionCostSource
from brain.recharge.models import BrainUsageContext


class OllamaExecutionCostSource(ExecutionCostSource):
    """
    Resolves the technical execution cost for local Ollama usage.

    V1 intentionally uses a configurable local cost rate rather than
    embedding pricing logic inside the LLM provider.
    """

    def __init__(
        self,
        input_token_cost: Decimal,
        output_token_cost: Decimal,
        version: str = "v1",
    ):
        if input_token_cost < Decimal("0"):
            raise ValueError(
                "Input token cost cannot be negative."
            )

        if output_token_cost < Decimal("0"):
            raise ValueError(
                "Output token cost cannot be negative."
            )

        if not version.strip():
            raise ValueError(
                "Cost source version is required."
            )

        self._input_token_cost = input_token_cost
        self._output_token_cost = output_token_cost
        self._version = version

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def version(self) -> str:
        return self._version

    def resolve(
        self,
        context: BrainUsageContext,
    ) -> ExecutionCost | None:
        if context.provider != "ollama":
            return None

        if context.input_tokens is None:
            return None

        if context.output_tokens is None:
            return None

        if context.input_tokens < 0:
            raise ValueError(
                "Input token count cannot be negative."
            )

        if context.output_tokens < 0:
            raise ValueError(
                "Output token count cannot be negative."
            )

        input_cost = (
            Decimal(context.input_tokens)
            * self._input_token_cost
        )

        output_cost = (
            Decimal(context.output_tokens)
            * self._output_token_cost
        )

        total_cost = input_cost + output_cost

        return ExecutionCost(
            amount=total_cost,
            currency="USD",
            source=self.name,
            version=self.version,
            metadata={
                "provider": context.provider,
                "model": context.model,
                "input_tokens": context.input_tokens,
                "output_tokens": context.output_tokens,
            },
        )