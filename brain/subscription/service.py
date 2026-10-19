from datetime import datetime

from brain.subscription.models import (
    Subscription,
    SubscriptionStatus,
    PAID_BRAIN_TIERS,
)
from brain.subscription.repository import SubscriptionRepository
from brain.tier.models import BrainTier


class SubscriptionService:

    def __init__(
        self,
        repository: SubscriptionRepository,
    ):
        if repository is None:
            raise ValueError("Subscription repository is required.")

        self._repository = repository

    def get_subscription(
        self,
        user_id: int,
    ) -> Subscription | None:
        if user_id <= 0:
            raise ValueError("User ID must be positive.")

        return self._repository.get_by_user_id(user_id)

    def activate(
        self,
        user_id: int,
        tier: BrainTier,
        started_at: datetime,
        current_period_started_at: datetime,
        current_period_ends_at: datetime,
    ) -> Subscription:

        if user_id <= 0:
            raise ValueError("User ID must be positive.")

        if tier not in PAID_BRAIN_TIERS:
            raise ValueError(
                "Subscription requires a paid Brain Tier."
            )

        if current_period_ends_at <= current_period_started_at:
            raise ValueError(
                "Subscription period end must be after period start."
            )

        existing = self._repository.get_by_user_id(user_id)

        subscription = Subscription(
            user_id=user_id,
            tier=tier,
            status=SubscriptionStatus.ACTIVE,
            started_at=(
                min(existing.started_at, current_period_started_at)
                if existing is not None
                else min(started_at, current_period_started_at)

            ),
            current_period_started_at=current_period_started_at,
            current_period_ends_at=current_period_ends_at,
        )

        if existing is not None:
            return self._repository.update(subscription)

        return self._repository.create(subscription)

    def cancel(
        self,
        user_id: int,
    ) -> Subscription:

        if user_id <= 0:
            raise ValueError("User ID must be positive.")

        existing = self._repository.get_by_user_id(user_id)

        if existing is None:
            raise ValueError("Subscription not found.")

        if existing.status == SubscriptionStatus.CANCELLED:
            return existing

        cancelled = Subscription(
            user_id=existing.user_id,
            tier=existing.tier,
            status=SubscriptionStatus.CANCELLED,
            started_at=existing.started_at,
            current_period_started_at=existing.current_period_started_at,
            current_period_ends_at=existing.current_period_ends_at,
        )

        return self._repository.update(cancelled)