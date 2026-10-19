from datetime import datetime, timedelta, timezone
from decimal import Decimal

from brain.subscription.activation import SubscriptionActivationService
from brain.subscription.repository import SubscriptionRepository
from brain.subscription.service import SubscriptionService
from brain.tier.capacity.activation import TierCapacityActivationService
from brain.tier.capacity.coordinator import TierCapacityCoordinator
from brain.tier.capacity.period import TierCapacityPeriodResolver
from brain.tier.capacity.provisioning import (
    TierCapacityProvisioningService,
)
from brain.tier.capacity.repository import TierBrainCapacityRepository
from brain.tier.entitlement.service import TierEntitlementService
from brain.tier.models import BrainTier
from database.database import SessionLocal
from brain.subscription.subscription_model import SubscriptionModel
from brain.tier.capacity.capacity_model import TierBrainCapacityModel



def test_subscription_activation_provisions_subscription_and_capacity():
    user_id = 999977

    session = SessionLocal()

    try:

        session.query(TierBrainCapacityModel).filter(
            TierBrainCapacityModel.user_id == user_id
        ).delete()

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



        provisioning_service = TierCapacityProvisioningService(
            repository=capacity_repository,
        )

        period_resolver = TierCapacityPeriodResolver(
            entitlement_service=entitlement_service,
        )

        coordinator = TierCapacityCoordinator(
            entitlement_service=entitlement_service,
            provisioning_service=provisioning_service,
            period_resolver=period_resolver,
        )

        capacity_activation_service = TierCapacityActivationService(
            coordinator=coordinator,
        )

        activation_service = SubscriptionActivationService(
            subscription_service=subscription_service,
            tier_capacity_activation_service=capacity_activation_service,
        )

        period_started_at = datetime.now(timezone.utc)
        period_ends_at = period_started_at + timedelta(days=30)

        subscription = activation_service.activate(
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            started_at=period_started_at,
            current_period_started_at=period_started_at,
            current_period_ends_at=period_ends_at,
        )

        assert subscription.user_id == user_id
        assert subscription.tier == BrainTier.THALAMUS

        capacity = capacity_repository.get(user_id)

        assert capacity is not None
        assert capacity.user_id == user_id
        assert capacity.tier == BrainTier.THALAMUS
        assert capacity.allowance == Decimal("3000")
        assert capacity.consumed == Decimal("0")
        assert capacity.remaining == Decimal("3000")

        session.commit()

    finally:
        session.rollback()
        session.close()