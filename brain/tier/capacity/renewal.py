from datetime import datetime
from decimal import Decimal

from brain.tier.entitlement.service import TierEntitlementService
from brain.tier.models import BrainTier

from .models import TierBrainCapacity
from .repository import TierBrainCapacityRepository


PAID_BRAIN_TIERS = frozenset({
    BrainTier.STARTER,
    BrainTier.BRAIN_MINI,
    BrainTier.BRAIN_ORION,
    BrainTier.THALAMUS,
    BrainTier.HIPPOCAMPUS,
})


class TierCapacityRenewalService:
    """
    Renews included Brain capacity for an existing paid-tier user.

    Renewal resets included capacity consumption for the new period.
    Wallet balance is handled independently.
    """

    def __init__(
        self,
        repository: TierBrainCapacityRepository,
        entitlement_service: TierEntitlementService,
    ):
        if repository is None:
            raise ValueError(
                "Tier Brain capacity repository is required."
            )

        if entitlement_service is None:
            raise ValueError(
                "Tier entitlement service is required."
            )

        self._repository = repository
        self._entitlement_service = entitlement_service

    def renew(
        self,
        user_id: int,
        tier: BrainTier,
        period_started_at: datetime,
        period_ends_at: datetime,
    ) -> TierBrainCapacity:

        if user_id <= 0:
            raise ValueError(
                "User ID must be greater than zero."
            )

        if tier not in PAID_BRAIN_TIERS:
            raise ValueError(
                "Capacity renewal requires a paid Brain tier."
            )

        if period_started_at is None:
            raise ValueError("Period start is required.")

        if period_ends_at is None:
            raise ValueError("Period end is required.")

        if period_ends_at <= period_started_at:
            raise ValueError(
                "Period end must be after period start."
            )

        entitlement = self._entitlement_service.get_entitlement(
            tier
        )

        existing = self._repository.get(user_id)

        if existing is None:
            raise ValueError(
                "Tier Brain capacity does not exist."
            )

        if existing.tier != tier:
            raise ValueError(
                "Capacity renewal does not allow a tier change."
            )
        if (
            period_started_at == existing.period_started_at
            and period_ends_at == existing.period_ends_at
):
            raise ValueError(
                "Capacity has already been renewed for this period."
    )



        renewed_capacity = TierBrainCapacity(
            user_id=user_id,
            tier=tier,
            allowance=Decimal(
                str(entitlement.included_brain_units)
            ),
            consumed=Decimal("0"),
            period_started_at=period_started_at,
            period_ends_at=period_ends_at,
        )

        return self._repository.update(renewed_capacity)