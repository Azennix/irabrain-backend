from datetime import datetime, timedelta, timezone

from brain.tier.entitlement.models import TierResetPeriod
from brain.tier.entitlement.service import TierEntitlementService
from brain.tier.models import BrainTier


class TierCapacityPeriodResolver:
    """
    Resolves the included Brain capacity period.

    FREE tiers can derive their period from the entitlement reset rule.
    Paid billing-cycle periods must be supplied by the subscription system.
    """

    def __init__(
        self,
        entitlement_service: TierEntitlementService,
    ):
        if entitlement_service is None:
            raise ValueError(
                "Tier entitlement service is required."
            )

        self._entitlement_service = entitlement_service

    def resolve(
        self,
        tier: BrainTier,
        period_started_at: datetime | None = None,
        billing_period_ends_at: datetime | None = None,
    ) -> tuple[datetime, datetime]:

        entitlement = (
            self._entitlement_service.get_entitlement(tier)
        )

        start = (
            period_started_at
            or datetime.now(timezone.utc)
        )

        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        else:
            start = start.astimezone(timezone.utc)

        if entitlement.reset_period == TierResetPeriod.HOURLY:
            if entitlement.reset_interval_hours is None:
                raise ValueError(
                    "Hourly tier reset requires an interval."
                )

            end = start + timedelta(
                hours=entitlement.reset_interval_hours
            )

            return start, end

        if entitlement.reset_period == TierResetPeriod.BILLING_CYCLE:
            if billing_period_ends_at is None:
                raise ValueError(
                    "Billing-cycle period end is required."
                )

            end = billing_period_ends_at

            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            else:
                end = end.astimezone(timezone.utc)

            if end <= start:
                raise ValueError(
                    "Billing period end must be after period start."
                )

            return start, end

        raise ValueError(
            f"Unsupported tier reset period: "
            f"{entitlement.reset_period}"
        )