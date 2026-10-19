from datetime import datetime

from brain.subscription.models import Subscription
from brain.subscription.repository import SubscriptionRepository
from brain.tier.capacity.renewal import TierCapacityRenewalService
from brain.tier.models import BrainTier


class SubscriptionRenewalService:

    def __init__(
        self,
        repository: SubscriptionRepository,
        tier_capacity_renewal_service: TierCapacityRenewalService,
    ):
        if repository is None:
            raise ValueError("Subscription repository is required.")

        if tier_capacity_renewal_service is None:
            raise ValueError(
                "Tier capacity renewal service is required."
            )

        self._repository = repository
        self._tier_capacity_renewal_service = (
            tier_capacity_renewal_service
        )

    def renew(
        self,
        user_id: int,
        tier: BrainTier,
        current_period_started_at: datetime,
        current_period_ends_at: datetime,
    ) -> Subscription:

        if user_id <= 0:
            raise ValueError("User ID must be positive.")

        existing = self._repository.get_by_user_id(user_id,for_update=True,)

        if existing is None:
            raise ValueError("Subscription not found.")

        if existing.tier != tier:
            raise ValueError(
                "Subscription tier does not match renewal tier."
            )
        if current_period_started_at is None or current_period_ends_at is None:
            raise ValueError("Renewal period boundaries are required.")

        if current_period_ends_at <= current_period_started_at:
            raise ValueError(
                "Renewal period end must be after its start."
    )

        if existing.current_period_ends_at is not None:
            if current_period_started_at < existing.current_period_ends_at:
                raise ValueError(
                    "Renewal period must not overlap the existing billing period."
        )

        renewed = Subscription(
            user_id=existing.user_id,
            tier=existing.tier,
            status=existing.status,
            started_at=existing.started_at,
            current_period_started_at=current_period_started_at,
            current_period_ends_at=current_period_ends_at,
        )

        updated = self._repository.update(renewed)

        self._tier_capacity_renewal_service.renew(
            user_id=user_id,
            tier=tier,
            period_started_at=current_period_started_at,
            period_ends_at=current_period_ends_at,
        )

        return updated