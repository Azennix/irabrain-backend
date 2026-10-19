from datetime import datetime
from decimal import Decimal

from brain.tier.models import BrainTier

from .models import TierBrainCapacity
from .repository import TierBrainCapacityRepository


class TierCapacityProvisioningService:
    """
    Creates or updates the included Brain capacity for a user's tier.
    Billing/subscription systems provide the period boundaries.
    """

    def __init__(
        self,
        repository: TierBrainCapacityRepository,
    ):
        if repository is None:
            raise ValueError(
                "Tier Brain capacity repository is required."
            )

        self._repository = repository

    def provision(
        self,
        user_id: int,
        tier: BrainTier,
        allowance: Decimal,
        period_started_at: datetime,
        period_ends_at: datetime,
    ) -> TierBrainCapacity:

        if user_id <= 0:
            raise ValueError(
                "User ID must be greater than zero."
            )

        if tier is None:
            raise ValueError("Brain Tier is required.")

        if allowance <= Decimal("0"):
            raise ValueError(
                "Allowance must be greater than zero."
            )

        if period_started_at is None or period_ends_at is None:
            raise ValueError("Billing period boundaries are required.")

        if period_ends_at <= period_started_at:
            raise ValueError(
                "Billing period end must be after its start."
            )

        existing = self._repository.get(user_id)

        if existing is None:
            capacity = TierBrainCapacity(
                user_id=user_id,
                tier=tier,
                allowance=allowance,
                consumed=Decimal("0"),
                period_started_at=period_started_at,
                period_ends_at=period_ends_at,
            )
            return self._repository.create(capacity)

        # Preserve usage during an upgrade within the same period.
        # Reset usage when a genuinely new billing period begins.
# Preserve usage when updating the tier within the same period.
        same_period = (
            existing.period_started_at == period_started_at
            and existing.period_ends_at == period_ends_at
)

        if same_period:
            updated_consumed = min(existing.consumed, allowance)
        else:
            updated_consumed = Decimal("0")

        updated_capacity = TierBrainCapacity(
            user_id=user_id,
            tier=tier,
            allowance=allowance,
            consumed=updated_consumed,
            period_started_at=period_started_at,
            period_ends_at=period_ends_at,
        )

        return self._repository.update(updated_capacity)