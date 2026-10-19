from decimal import Decimal

from brain.recharge.cost.ollama_cost_source import (
    OllamaExecutionCostSource,
)
from brain.recharge.models import BrainUsageContext


def test_ollama_cost_source_calculates_execution_cost():
    source = OllamaExecutionCostSource(
        input_token_cost=Decimal("0.001"),
        output_token_cost=Decimal("0.002"),
    )

    context = BrainUsageContext(
        request_id="ollama-cost-test-001",
        user_id=1001,
        provider="ollama",
        model="qwen2.5:7b",
        input_tokens=100,
        output_tokens=50,
    )

    result = source.resolve(context)

    assert result is not None
    assert result.amount == Decimal("0.20")
    assert result.currency == "USD"
    assert result.source == "ollama"
    assert result.version == "v1"


def test_ollama_cost_source_ignores_other_providers():
    source = OllamaExecutionCostSource(
        input_token_cost=Decimal("0.001"),
        output_token_cost=Decimal("0.002"),
    )

    context = BrainUsageContext(
        request_id="other-provider-test-001",
        user_id=1001,
        provider="openai",
        model="future-model",
        input_tokens=100,
        output_tokens=50,
    )

    result = source.resolve(context)

    assert result is None


def test_ollama_cost_source_returns_none_without_token_usage():
    source = OllamaExecutionCostSource(
        input_token_cost=Decimal("0.001"),
        output_token_cost=Decimal("0.002"),
    )

    context = BrainUsageContext(
        request_id="missing-usage-test-001",
        user_id=1001,
        provider="ollama",
        model="qwen2.5:7b",
        input_tokens=None,
        output_tokens=None,
    )

    result = source.resolve(context)

    assert result is None