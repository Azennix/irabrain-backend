from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from brain.tier.capabilities import Capability
from brain.tier.models import BrainTier


class TierUsagePolicy(str, Enum):
    LIMITED = "limited"
    STANDARD = "standard"
    HIGH = "high"


class TierResetPeriod(str, Enum):
    HOURLY = "hourly"
    BILLING_CYCLE = "billing_cycle"


@dataclass(frozen=True, slots=True)
class TierEntitlement:
    tier: BrainTier
    allowed_capabilities: frozenset[Capability]
    max_context_window: int
    max_complexity: float
    usage_policy: TierUsagePolicy
    included_brain_units: Decimal
    reset_period: TierResetPeriod
    reset_interval_hours: int | None = None
    version: str = "v1"

    def __post_init__(self) -> None:
        if self.max_context_window < 0:
            raise ValueError(
                "max_context_window cannot be negative."
            )

        if not 0.0 <= self.max_complexity <= 1.0:
            raise ValueError(
                "max_complexity must be between 0.0 and 1.0."
            )

        if self.included_brain_units <= 0:
            raise ValueError(
                "included_brain_units must be greater than zero."
            )

        if self.reset_period == TierResetPeriod.HOURLY:
            if self.reset_interval_hours is None:
                raise ValueError(
                    "Hourly reset requires reset_interval_hours."
                )

            if self.reset_interval_hours <= 0:
                raise ValueError(
                    "reset_interval_hours must be greater than zero."
                )

        elif self.reset_period == TierResetPeriod.BILLING_CYCLE:
            if self.reset_interval_hours is not None:
                raise ValueError(
                    "Billing-cycle reset must not use reset_interval_hours."
                )

        else:
            raise ValueError(
                f"Unsupported tier reset period: {self.reset_period}"
            )