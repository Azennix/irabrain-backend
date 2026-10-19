from datetime import datetime, timezone
from decimal import Decimal

from .models import TierBrainCapacity
from .policy import (
    CapacityConsumptionResult,
    TierCapacityConsumptionPolicy,
)


class TierCapacityService:
    """
    Handles tier-included Brain capacity consumption.

    This service is intentionally independent from:
    - wallet/payment logic
    - settlement logic
    - subscription billing
    """

    def consume(
        self,
        capacity: TierBrainCapacity,
        requested_units: Decimal,
        now: datetime | None = None,
    ) -> tuple[TierBrainCapacity, CapacityConsumptionResult]:

        if capacity is None:
            raise ValueError("Tier Brain capacity is required.")

        current_time = now or datetime.now(timezone.utc)

        if current_time >= capacity.period_ends_at:
            raise ValueError(
                "Tier Brain capacity period has expired."
            )

        result = TierCapacityConsumptionPolicy.calculate(
            capacity=capacity,
            requested_units=requested_units,
        )

        updated_capacity = TierBrainCapacity(
            user_id=capacity.user_id,
            tier=capacity.tier,
            allowance=capacity.allowance,
            consumed=capacity.consumed + result.consumed,
            period_started_at=capacity.period_started_at,
            period_ends_at=capacity.period_ends_at,
        )

        return updated_capacity, result