from decimal import Decimal

from brain.recharge.cost.cost_calculator import (
    CostBasedBrainUnitCalculator,
)
from brain.recharge.cost.cost_resolver import ExecutionCostResolver
from brain.recharge.cost.passthrough_cost_source import (
    PassthroughExecutionCostSource,
)
from brain.recharge.models import BrainUsageContext


def test_cost_based_brain_unit_calculation():
    resolver = ExecutionCostResolver(
        sources=[PassthroughExecutionCostSource()]
    )

    calculator = CostBasedBrainUnitCalculator(
        cost_resolver=resolver,
        unit_cost=Decimal("0.10"),
        calculation_version="v1",
    )

    context = BrainUsageContext(
        request_id="integration-test-1",
        user_id=1,
        provider="test-provider",
        model="test-model",
        estimated_cost=0.25,
    )

    result = calculator.calculate(context)

    assert result.units == 2.5
    assert result.calculation_version == "v1"
    assert result.basis == "execution_cost"
    assert result.metadata["cost_source"] == "passthrough"
    assert result.metadata["cost_version"] == "v1"
    assert result.metadata["cost_currency"] == "USD"