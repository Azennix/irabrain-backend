from decimal import Decimal

from brain.recharge.cost.ollama_cost_source import (
    OllamaExecutionCostSource,
)
from brain.recharge.cost.cost_resolver import ExecutionCostResolver
from brain.recharge.models import BrainUsageContext


def test_resolver_uses_ollama_cost_source():
    resolver = ExecutionCostResolver(
        sources=[
            OllamaExecutionCostSource(
                input_token_cost=Decimal("0.001"),
                output_token_cost=Decimal("0.002"),
            ),
        ]
    )

    context = BrainUsageContext(
        request_id="ollama-resolver-test-001",
        user_id=1001,
        provider="ollama",
        model="qwen2.5:7b",
        input_tokens=100,
        output_tokens=50,
    )

    result = resolver.resolve(context)

    assert result.amount == Decimal("0.20")
    assert result.currency == "USD"
    assert result.source == "ollama"
    assert result.version == "v1"