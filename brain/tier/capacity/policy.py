from dataclasses import dataclass
from decimal import Decimal

from .models import TierBrainCapacity


@dataclass(frozen=True, slots=True)
class CapacityConsumptionResult:
    requested: Decimal
    consumed: Decimal
    remaining: Decimal
    fully_consumed: bool


class TierCapacityConsumptionPolicy:
    """
    Calculates how much requested Brain capacity can be consumed
    from a tier's included capacity.
    """

    @staticmethod
    def calculate(
        capacity: TierBrainCapacity,
        requested_units: Decimal,
    ) -> CapacityConsumptionResult:

        if capacity is None:
            raise ValueError("Tier Brain capacity is required.")

        if requested_units <= Decimal("0"):
            raise ValueError(
                "requested_units must be greater than zero."
            )

        available = capacity.remaining

        consumed = min(
            requested_units,
            available,
        )

        remaining = available - consumed

        return CapacityConsumptionResult(
            requested=requested_units,
            consumed=consumed,
            remaining=remaining,
            fully_consumed=consumed >= requested_units,
        )