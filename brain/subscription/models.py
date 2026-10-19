from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from brain.tier.models import BrainTier


PAID_BRAIN_TIERS = frozenset({
    BrainTier.STARTER,
    BrainTier.BRAIN_MINI,
    BrainTier.BRAIN_ORION,
    BrainTier.THALAMUS,
    BrainTier.HIPPOCAMPUS,
})


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class Subscription:
    user_id: int
    tier: BrainTier
    status: SubscriptionStatus
    started_at: datetime
    current_period_started_at: datetime
    current_period_ends_at: datetime

    def __post_init__(self) -> None:
        if self.user_id <= 0:
            raise ValueError("User ID must be positive.")

        if self.tier not in PAID_BRAIN_TIERS:
            raise ValueError(
                "Subscription requires a paid Brain Tier."
            )

        if (
            self.current_period_ends_at
            <= self.current_period_started_at
        ):
            raise ValueError(
                "Subscription period end must be after period start."
            )

        if self.started_at > self.current_period_started_at:
            raise ValueError(
                "Subscription start cannot be after "
                "the current period start."
            )