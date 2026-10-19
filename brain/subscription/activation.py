from datetime import datetime

from database.user_repository import UserRepository

from brain.subscription.service import SubscriptionService
from brain.tier.capacity.activation import TierCapacityActivationService
from brain.tier.models import BrainTier


class SubscriptionActivationService:

    def __init__(
        self,
        subscription_service: SubscriptionService,
        tier_capacity_activation_service: TierCapacityActivationService,
        user_repository: UserRepository,
    ):
        if subscription_service is None:
            raise ValueError("Subscription service is required.")

        if tier_capacity_activation_service is None:
            raise ValueError(
                "Tier capacity activation service is required."
            )

        if user_repository is None:
            raise ValueError("User repository is required.")

        self._subscription_service = subscription_service
        self._tier_capacity_activation_service = (
            tier_capacity_activation_service
        )
        self._user_repository = user_repository

    def activate(
        self,
        user_id: int,
        tier: BrainTier,
        started_at: datetime,
        current_period_started_at: datetime,
        current_period_ends_at: datetime,
    ):
        paid_tiers = {
            BrainTier.STARTER,
            BrainTier.BRAIN_MINI,
            BrainTier.BRAIN_ORION,
            BrainTier.THALAMUS,
            BrainTier.HIPPOCAMPUS,
        }

        if tier not in paid_tiers:
            raise ValueError(
                "Subscription activation requires a paid Brain Tier."
            )


        if started_at is None:
            raise ValueError("Subscription start time is required.")

        if current_period_started_at is None or current_period_ends_at is None:
            raise ValueError("Billing period boundaries are required.")

        if current_period_ends_at <= current_period_started_at:
            raise ValueError(
                "Billing period end must be after its start."
    )

         # Ensure the user exists before activating the subscription.#
        user = self._user_repository.get_by_id(user_id)

        if user is None:
            raise ValueError(f"User not found: {user_id}")

        tier_rank = {
            BrainTier.FREE: 0,
            BrainTier.STARTER: 1,
            BrainTier.BRAIN_MINI: 2,
            BrainTier.BRAIN_ORION: 3,
            BrainTier.THALAMUS: 4,
            BrainTier.HIPPOCAMPUS: 5,
        }

        current_tier = BrainTier(user.brain_tier)

        # A lower-tier purchase must not replace the existing
        # subscription or reset the higher tier's included capacity.
        if tier_rank[tier] < tier_rank[current_tier]:
            existing_subscription = (
                self._subscription_service.get_subscription(user_id)
            )

            if existing_subscription is None:
                raise ValueError(
                    "Active Brain Tier has no corresponding subscription."
                )

            return existing_subscription

        subscription = self._subscription_service.activate(
            user_id=user_id,
            tier=tier,
            started_at=started_at,
            current_period_started_at=current_period_started_at,
            current_period_ends_at=current_period_ends_at,
        )

        self._tier_capacity_activation_service.activate(
            user_id=user_id,
            tier=tier,
            billing_period_started_at=current_period_started_at,
            billing_period_ends_at=current_period_ends_at,
        )




        tier_rank = {
            BrainTier.FREE: 0,
            BrainTier.STARTER: 1,
            BrainTier.BRAIN_MINI: 2,
            BrainTier.BRAIN_ORION: 3,
            BrainTier.THALAMUS: 4,
            BrainTier.HIPPOCAMPUS: 5,
}

        current_tier = BrainTier(user.brain_tier)

        if tier_rank[tier] > tier_rank[current_tier]:
            self._user_repository.update_brain_tier(
                user_id=user_id,
                tier=tier.value,
    )

        return subscription