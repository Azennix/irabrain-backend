from datetime import datetime, timedelta, timezone
from decimal import Decimal

from brain.subscription.models import SubscriptionStatus
from brain.subscription.repository import SubscriptionRepository
from brain.subscription.renewal import SubscriptionRenewalService
from brain.subscription.service import SubscriptionService
from brain.tier.capacity.capacity_model import TierBrainCapacityModel
from brain.tier.capacity.renewal import TierCapacityRenewalService
from brain.tier.capacity.repository import TierBrainCapacityRepository
from brain.tier.entitlement.service import TierEntitlementService
from brain.tier.models import BrainTier
from database.database import SessionLocal


def test_subscription_renewal_resets_tier_capacity():
    user_id = 999978

    session = SessionLocal()

    try:
        session.query(TierBrainCapacityModel).filter(
            TierBrainCapacityModel.user_id == user_id
        ).delete()

        from brain.subscription.subscription_model import SubscriptionModel

        session.query(SubscriptionModel).filter(
            SubscriptionModel.user_id == user_id
        ).delete()

        session.commit()

        subscription_repository = SubscriptionRepository(session)
        subscription_service = SubscriptionService(
            repository=subscription_repository,
        )

        capacity_repository = TierBrainCapacityRepository(session)
        entitlement_service = TierEntitlementService()

        capacity_renewal_service = TierCapacityRenewalService(
            repository=capacity_repository,
            entitlement_service=entitlement_service,
        )

        renewal_service = SubscriptionRenewalService(
            repository=subscription_repository,
            tier_capacity_renewal_service=capacity_renewal_service,
        )

        first_period_start = datetime.now(timezone.utc)
        first_period_end = first_period_start + timedelta(days=30)

        subscription_service.activate(
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            started_at=first_period_start,
            current_period_started_at=first_period_start,
            current_period_ends_at=first_period_end,
        )

        capacity = capacity_repository.get(user_id)

        if capacity is None:
            from brain.tier.capacity.provisioning import (
                TierCapacityProvisioningService,
            )

            provisioning_service = TierCapacityProvisioningService(
                repository=capacity_repository,
            )

            provisioning_service.provision(
                user_id=user_id,
                tier=BrainTier.THALAMUS,
                allowance=Decimal("3000"),
                period_started_at=first_period_start,
                period_ends_at=first_period_end,
            )

        capacity = capacity_repository.get(user_id)

        consumed_capacity = capacity_repository.update(
            capacity.__class__(
                user_id=capacity.user_id,
                tier=capacity.tier,
                allowance=capacity.allowance,
                consumed=Decimal("500"),
                period_started_at=capacity.period_started_at,
                period_ends_at=capacity.period_ends_at,
            )
        )

        second_period_start = first_period_end
        second_period_end = second_period_start + timedelta(days=30)

        renewed = renewal_service.renew(
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            current_period_started_at=second_period_start,
            current_period_ends_at=second_period_end,
        )

        assert renewed.user_id == user_id
        assert renewed.tier == BrainTier.THALAMUS
        assert renewed.status == SubscriptionStatus.ACTIVE
        assert renewed.current_period_started_at == second_period_start
        assert renewed.current_period_ends_at == second_period_end

        renewed_capacity = capacity_repository.get(user_id)

        assert renewed_capacity is not None
        assert renewed_capacity.tier == BrainTier.THALAMUS
        assert renewed_capacity.allowance == Decimal("3000")
        assert renewed_capacity.consumed == Decimal("0")
        assert renewed_capacity.remaining == Decimal("3000")
        assert renewed_capacity.period_started_at == second_period_start
        assert renewed_capacity.period_ends_at == second_period_end

        session.commit()

    finally:
        session.rollback()
        session.close()