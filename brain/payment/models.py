from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

from brain.tier.models import BrainTier


class PaymentStatus(str, Enum):
    CREATED = "created"
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


PAID_BRAIN_TIERS = frozenset({
    BrainTier.STARTER,
    BrainTier.BRAIN_MINI,
    BrainTier.BRAIN_ORION,
    BrainTier.THALAMUS,
    BrainTier.HIPPOCAMPUS,
})


@dataclass(frozen=True, slots=True)
class Payment:
    payment_id: int | None
    user_id: int
    tier: BrainTier
    amount: Decimal
    currency: str
    status: PaymentStatus
    provider: str
    provider_order_id: str | None
    provider_payment_id: str | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.user_id <= 0:
            raise ValueError("User ID must be positive.")

        if self.tier not in PAID_BRAIN_TIERS:
            raise ValueError(
                "Payment requires a paid Brain Tier."
            )

        if self.amount <= Decimal("0"):
            raise ValueError(
                "Payment amount must be positive."
            )

        if not self.currency:
            raise ValueError(
                "Payment currency is required."
            )

        if not self.provider:
            raise ValueError(
                "Payment provider is required."
            )

        if not self.provider_order_id:
            raise ValueError("Provider order ID is required.")

        if self.created_at is None:
            raise ValueError(
                "Payment creation time is required."
            )

        if self.updated_at is None:
            raise ValueError(
                "Payment update time is required."
            )