from decimal import Decimal

from brain.recharge.cost.passthrough_cost_source import (
    PassthroughExecutionCostSource,
)
from brain.recharge.models import BrainUsageContext


def test_passthrough_source_resolves_existing_cost():
    source = PassthroughExecutionCostSource()

    context = BrainUsageContext(
        request_id="request-1",
        provider="test-provider",
        model="test-model",
        estimated_cost=0.25,
        metadata={
            "cost_currency": "USD",
        },
    )

    result = source.resolve(context)

    assert result is not None
    assert result.amount == Decimal("0.25")
    assert result.currency == "USD"
    assert result.source == "passthrough"
    assert result.version == "v1"


def test_passthrough_source_returns_none_without_cost():
    source = PassthroughExecutionCostSource()

    context = BrainUsageContext(
        request_id="request-2",
        provider="test-provider",
        model="test-model",
    )

    result = source.resolve(context)

    assert result is None


def test_passthrough_source_rejects_negative_cost():
    source = PassthroughExecutionCostSource()

    context = BrainUsageContext(
        request_id="request-3",
        provider="test-provider",
        model="test-model",
        estimated_cost=-0.10,
    )

    try:
        source.resolve(context)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "cannot be negative" in str(exc)