from dataclasses import dataclass
from decimal import Decimal

from brain.recharge.entitlement.models import FreeBrainEntitlement


@dataclass(frozen=True, slots=True)
class FreeBrainConsumptionResult:
    consumed: Decimal
    remaining: Decimal
    fully_consumed: bool


class FreeBrainConsumptionPolicy:
    """
    Determines how much of a requested Brain Unit amount
    can be consumed from the user's free entitlement.

    This policy does not modify the database.
    """

    def calculate(
        self,
        entitlement: FreeBrainEntitlement,
        requested_units: Decimal,
    ) -> FreeBrainConsumptionResult:
        if entitlement is None:
            raise ValueError(
                "Free Brain entitlement is required."
            )

        if requested_units <= 0:
            raise ValueError(
                "Requested Brain Units must be greater than zero."
            )

        remaining = entitlement.allowance - entitlement.consumed

        if remaining < 0:
            raise ValueError(
                "Free Brain entitlement has an invalid balance."
            )

        free_consumption = min(
            requested_units,
            remaining,
        )

        remaining_after = remaining - free_consumption

        return FreeBrainConsumptionResult(
            consumed=free_consumption,
            remaining=remaining_after,
            fully_consumed=free_consumption == requested_units,
        )