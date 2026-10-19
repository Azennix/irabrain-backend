from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from brain.tier.models import BrainTier


@dataclass(frozen=True, slots=True)
class TierBrainCapacity:
    """
    Represents the included Brain capacity available to a user
    through their current Brain Tier.
    """

    user_id: int
    tier: BrainTier
    allowance: Decimal
    consumed: Decimal
    period_started_at: datetime
    period_ends_at: datetime

    @property
    def remaining(self) -> Decimal:
        remaining = self.allowance - self.consumed

        if remaining < Decimal("0"):
            return Decimal("0")

        return remaining

    def __post_init__(self) -> None:
        if self.user_id <= 0:
            raise ValueError("user_id must be greater than zero.")

        if self.allowance <= Decimal("0"):
            raise ValueError(
                "allowance must be greater than zero."
            )

        if self.consumed < Decimal("0"):
            raise ValueError(
                "consumed cannot be negative."
            )

        if self.consumed > self.allowance:
            raise ValueError(
                "consumed cannot exceed allowance."
            )

        if self.period_ends_at <= self.period_started_at:
            raise ValueError(
                "period_ends_at must be after period_started_at."
            )