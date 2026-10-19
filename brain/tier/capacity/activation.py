from datetime import datetime

from brain.tier.models import BrainTier

from .coordinator import TierCapacityCoordinator
from .models import TierBrainCapacity


PAID_BRAIN_TIERS = frozenset({
    BrainTier.STARTER,
    BrainTier.BRAIN_MINI,
    BrainTier.BRAIN_ORION,
    BrainTier.THALAMUS,
    BrainTier.HIPPOCAMPUS,
})


class TierCapacityActivationService:
    """
    Activates included Brain capacity for a paid Brain Tier.

    The subscription system provides the billing-period boundaries.
    This service does not know about Razorpay or payment processing.
    """

    def __init__(
        self,
        coordinator: TierCapacityCoordinator,
    ):
        if coordinator is None:
            raise ValueError(
                "Tier capacity coordinator is required."
            )

        self._coordinator = coordinator

    def activate(
        self,
        user_id: int,
        tier: BrainTier,
        billing_period_started_at: datetime,
        billing_period_ends_at: datetime,
    ) -> TierBrainCapacity:

        if user_id <= 0:
            raise ValueError(
                "User ID must be greater than zero."
            )

        if tier not in PAID_BRAIN_TIERS:
            raise ValueError(
                "Paid-tier activation requires a paid Brain Tier."
            )

        if billing_period_started_at is None:
            raise ValueError(
                "Billing period start is required."
            )

        if billing_period_ends_at is None:
            raise ValueError(
                "Billing period end is required."
            )

        if billing_period_ends_at <= billing_period_started_at:
            raise ValueError(
                "Billing period end must be after its start."
            )

        return self._coordinator.provision(
            user_id=user_id,
            tier=tier,
            period_started_at=billing_period_started_at,
            billing_period_ends_at=billing_period_ends_at,
        )