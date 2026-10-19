from datetime import datetime

from brain.tier.entitlement.service import TierEntitlementService
from brain.tier.models import BrainTier

from .models import TierBrainCapacity
from .period import TierCapacityPeriodResolver
from .provisioning import TierCapacityProvisioningService


class TierCapacityCoordinator:
    """
    Coordinates Brain Tier entitlement, period resolution,
    and included capacity provisioning.

    It does not own payment or subscription logic.
    """

    def __init__(
        self,
        entitlement_service: TierEntitlementService,
        provisioning_service: TierCapacityProvisioningService,
        period_resolver: TierCapacityPeriodResolver,
    ):
        if entitlement_service is None:
            raise ValueError(
                "Tier entitlement service is required."
            )

        if provisioning_service is None:
            raise ValueError(
                "Tier capacity provisioning service is required."
            )

        if period_resolver is None:
            raise ValueError(
                "Tier capacity period resolver is required."
            )

        self._entitlement_service = entitlement_service
        self._provisioning_service = provisioning_service
        self._period_resolver = period_resolver

    def provision(
        self,
        user_id: int,
        tier: BrainTier,
        period_started_at: datetime | None = None,
        billing_period_ends_at: datetime | None = None,
    ) -> TierBrainCapacity:

        entitlement = (
            self._entitlement_service.get_entitlement(tier)
        )

        start, end = self._period_resolver.resolve(
            tier=tier,
            period_started_at=period_started_at,
            billing_period_ends_at=billing_period_ends_at,
        )

        return self._provisioning_service.provision(
            user_id=user_id,
            tier=tier,
            allowance=entitlement.included_brain_units,
            period_started_at=start,
            period_ends_at=end,
        )