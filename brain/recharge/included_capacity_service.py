from datetime import datetime, timezone
from decimal import Decimal

from brain.recharge.entitlement.service import (
    FreeBrainEntitlementService,
)
from brain.tier.models import BrainTier
from brain.tier.capacity.capacity_service import (
    PersistentTierCapacityService,
)
from brain.tier.capacity.models import TierBrainCapacity



class IncludedBrainCapacityService:
    """
    Consumes Brain Units from the user's included tier capacity.

    FREE continues using the existing Free Brain entitlement.
    Paid tiers use the persisted tier capacity.
    """

    def __init__(
        self,
        free_brain_service: FreeBrainEntitlementService,
        tier_capacity_service: PersistentTierCapacityService,
    ):
        if free_brain_service is None:
            raise ValueError(
                "Free Brain service is required."
            )

        if tier_capacity_service is None:
            raise ValueError(
                "Tier capacity service is required."
            )

        self._free_brain_service = free_brain_service
        self._tier_capacity_service = tier_capacity_service

    def consume(
        self,
        user_id: int,
        tier: BrainTier,
        requested_units: Decimal,
    ) -> Decimal:

        if user_id <= 0:
            raise ValueError(
                "User ID must be greater than zero."
            )

        if tier is None:
            raise ValueError(
                "Brain Tier is required."
            )

        if requested_units <= Decimal("0"):
            raise ValueError(
                "Requested Brain Units must be greater than zero."
            )

        if tier == BrainTier.FREE:
            _, consumed, _ = self._free_brain_service.consume(
                user_id=user_id,
                requested_units=requested_units,
                now=datetime.now(timezone.utc),
            )

            return consumed

        _, result = self._tier_capacity_service.consume(
            user_id=user_id,
            requested_units=requested_units,
        )

        return result.consumed