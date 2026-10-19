from decimal import Decimal

from brain.recharge.cost.cost_resolver import ExecutionCostResolver
from brain.recharge.cost.cost_result import ExecutionCost
from brain.recharge.cost.cost_source import ExecutionCostSource
from brain.recharge.models import BrainUsageContext


class FakeCostSource(ExecutionCostSource):

    @property
    def name(self) -> str:
        return "test_source"

    @property
    def version(self) -> str:
        return "test-v1"

    def resolve(
        self,
        context: BrainUsageContext,
    ) -> ExecutionCost | None:
        if context.provider == "test-provider":
            return ExecutionCost(
                amount=Decimal("0.25"),
                currency="USD",
                source=self.name,
                version=self.version,
            )

        return None


def test_cost_resolver_resolves_cost():
    resolver = ExecutionCostResolver(
        sources=[FakeCostSource()]
    )

    context = BrainUsageContext(
        request_id="test-request-1",
        provider="test-provider",
        model="test-model",
    )

    result = resolver.resolve(context)

    assert result.amount == Decimal("0.25")
    assert result.currency == "USD"
    assert result.source == "test_source"
    assert result.version == "test-v1"


def test_cost_resolver_rejects_unresolved_cost():
    resolver = ExecutionCostResolver(
        sources=[FakeCostSource()]
    )

    context = BrainUsageContext(
        request_id="test-request-2",
        provider="unknown-provider",
        model="unknown-model",
    )

    try:
        resolver.resolve(context)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "No execution cost source" in str(exc)