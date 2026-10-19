from datetime import datetime, timedelta, timezone
from decimal import Decimal

from brain.tier.capacity.activation import TierCapacityActivationService
from brain.tier.capacity.capacity_model import TierBrainCapacityModel
from brain.tier.capacity.coordinator import TierCapacityCoordinator
from brain.tier.capacity.period import TierCapacityPeriodResolver
from brain.tier.capacity.provisioning import (
    TierCapacityProvisioningService,
)
from brain.tier.capacity.repository import TierBrainCapacityRepository
from brain.tier.entitlement.service import TierEntitlementService
from brain.tier.models import BrainTier
from database.database import SessionLocal


def test_thalamus_activation_provisions_included_capacity():
    user_id = 999973

    session = SessionLocal()

    try:
        repository = TierBrainCapacityRepository(session)
        entitlement_service = TierEntitlementService()
        provisioning_service = TierCapacityProvisioningService(
            repository=repository,
        )
        period_resolver = TierCapacityPeriodResolver(
            entitlement_service=entitlement_service,
        )

        coordinator = TierCapacityCoordinator(
            entitlement_service=entitlement_service,
            provisioning_service=provisioning_service,
            period_resolver=period_resolver,
        )

        activation_service = TierCapacityActivationService(
            coordinator=coordinator,
        )

        period_started_at = datetime.now(timezone.utc)
        period_ends_at = period_started_at + timedelta(days=30)

        activated = activation_service.activate(
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            billing_period_started_at=period_started_at,
            billing_period_ends_at=period_ends_at,
        )

        assert activated.user_id == user_id
        assert activated.tier == BrainTier.THALAMUS
        assert activated.allowance == Decimal("3000")
        assert activated.consumed == Decimal("0")
        assert activated.remaining == Decimal("3000")
        assert activated.period_started_at == period_started_at
        assert activated.period_ends_at == period_ends_at

        session.commit()

        persisted = (
            session.query(TierBrainCapacityModel)
            .filter(
                TierBrainCapacityModel.user_id == user_id
            )
            .first()
        )

        assert persisted is not None
        assert persisted.tier == BrainTier.THALAMUS.value
        assert Decimal(persisted.allowance) == Decimal("3000")
        assert Decimal(persisted.consumed) == Decimal("0")

    finally:
        session.rollback()
        session.close()