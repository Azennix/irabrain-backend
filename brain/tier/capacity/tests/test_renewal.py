import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from brain.tier.capacity.models import TierBrainCapacity
from brain.tier.capacity.renewal import TierCapacityRenewalService
from brain.tier.capacity.repository import TierBrainCapacityRepository
from brain.tier.entitlement.service import TierEntitlementService
from brain.tier.models import BrainTier
from database.database import SessionLocal


def test_thalamus_capacity_renews_with_fresh_allowance():
    user_id = 999980

    session = SessionLocal()

    try:
        repository = TierBrainCapacityRepository(session)
        entitlement_service = TierEntitlementService()

        now = datetime.now(timezone.utc)

        repository.create(
            TierBrainCapacity(
                user_id=user_id,
                tier=BrainTier.THALAMUS,
                allowance=Decimal("3000"),
                consumed=Decimal("2500"),
                period_started_at=now - timedelta(days=30),
                period_ends_at=now - timedelta(seconds=1),
            )
        )

        session.commit()

        renewal_service = TierCapacityRenewalService(
            repository=repository,
            entitlement_service=entitlement_service,
        )

        new_start = now
        new_end = now + timedelta(days=30)

        renewed = renewal_service.renew(
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            period_started_at=new_start,
            period_ends_at=new_end,
        )

        assert renewed.tier == BrainTier.THALAMUS
        assert renewed.allowance == Decimal("3000")
        assert renewed.consumed == Decimal("0")
        assert renewed.remaining == Decimal("3000")
        assert renewed.period_started_at == new_start
        assert renewed.period_ends_at == new_end

        session.commit()

    finally:
        session.rollback()
        session.close()



def test_hippocampus_capacity_renews_with_fresh_allowance():
    user_id = 999979

    session = SessionLocal()

    try:
        repository = TierBrainCapacityRepository(session)
        entitlement_service = TierEntitlementService()

        now = datetime.now(timezone.utc)

        repository.create(
            TierBrainCapacity(
                user_id=user_id,
                tier=BrainTier.HIPPOCAMPUS,
                allowance=Decimal("10000"),
                consumed=Decimal("8500"),
                period_started_at=now - timedelta(days=30),
                period_ends_at=now - timedelta(seconds=1),
            )
        )

        session.commit()

        renewal_service = TierCapacityRenewalService(
            repository=repository,
            entitlement_service=entitlement_service,
        )

        new_start = now
        new_end = now + timedelta(days=30)

        renewed = renewal_service.renew(
            user_id=user_id,
            tier=BrainTier.HIPPOCAMPUS,
            period_started_at=new_start,
            period_ends_at=new_end,
        )

        assert renewed.tier == BrainTier.HIPPOCAMPUS
        assert renewed.allowance == Decimal("10000")
        assert renewed.consumed == Decimal("0")
        assert renewed.remaining == Decimal("10000")
        assert renewed.period_started_at == new_start
        assert renewed.period_ends_at == new_end

        session.commit()

    finally:
        session.rollback()
        session.close()


def test_capacity_renewal_rejects_tier_change():
    user_id = 999977

    session = SessionLocal()

    try:
        repository = TierBrainCapacityRepository(session)
        entitlement_service = TierEntitlementService()

        now = datetime.now(timezone.utc)

        repository.create(
            TierBrainCapacity(
                user_id=user_id,
                tier=BrainTier.HIPPOCAMPUS,
                allowance=Decimal("10000"),
                consumed=Decimal("5000"),
                period_started_at=now - timedelta(days=30),
                period_ends_at=now - timedelta(seconds=1),
            )
        )

        session.commit()

        renewal_service = TierCapacityRenewalService(
            repository=repository,
            entitlement_service=entitlement_service,
        )

        with pytest.raises(
            ValueError,
            match="tier change",
        ):
            renewal_service.renew(
                user_id=user_id,
                tier=BrainTier.THALAMUS,
                period_started_at=now,
                period_ends_at=now + timedelta(days=30),
            )

    finally:
        session.rollback()
        session.close()


def test_capacity_renewal_rejects_invalid_period():
    user_id = 999976

    session = SessionLocal()

    try:
        repository = TierBrainCapacityRepository(session)
        entitlement_service = TierEntitlementService()

        now = datetime.now(timezone.utc)

        repository.create(
            TierBrainCapacity(
                user_id=user_id,
                tier=BrainTier.THALAMUS,
                allowance=Decimal("3000"),
                consumed=Decimal("1000"),
                period_started_at=now - timedelta(days=30),
                period_ends_at=now - timedelta(seconds=1),
            )
        )

        session.commit()

        renewal_service = TierCapacityRenewalService(
            repository=repository,
            entitlement_service=entitlement_service,
        )

        with pytest.raises(
            ValueError,
            match="Period end must be after period start",
        ):
            renewal_service.renew(
                user_id=user_id,
                tier=BrainTier.THALAMUS,
                period_started_at=now,
                period_ends_at=now,
            )

    finally:
        session.rollback()
        session.close()

def test_capacity_renewal_requires_existing_capacity():
    user_id = 999975

    session = SessionLocal()

    try:
        repository = TierBrainCapacityRepository(session)
        entitlement_service = TierEntitlementService()

        renewal_service = TierCapacityRenewalService(
            repository=repository,
            entitlement_service=entitlement_service,
        )

        now = datetime.now(timezone.utc)

        with pytest.raises(
            ValueError,
            match="Tier Brain capacity does not exist",
        ):
            renewal_service.renew(
                user_id=user_id,
                tier=BrainTier.THALAMUS,
                period_started_at=now,
                period_ends_at=now + timedelta(days=30),
            )

    finally:
        session.rollback()
        session.close()

def test_capacity_renewal_same_period_keeps_capacity_fresh():
    user_id = 999974

    session = SessionLocal()

    try:
        repository = TierBrainCapacityRepository(session)
        entitlement_service = TierEntitlementService()

        now = datetime.now(timezone.utc)
        new_start = now
        new_end = now + timedelta(days=30)

        repository.create(
            TierBrainCapacity(
                user_id=user_id,
                tier=BrainTier.THALAMUS,
                allowance=Decimal("3000"),
                consumed=Decimal("2500"),
                period_started_at=now - timedelta(days=30),
                period_ends_at=now - timedelta(seconds=1),
            )
        )

        session.commit()

        renewal_service = TierCapacityRenewalService(
            repository=repository,
            entitlement_service=entitlement_service,
        )

        first = renewal_service.renew(
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            period_started_at=new_start,
            period_ends_at=new_end,
        )

        session.commit()

        assert first.consumed == Decimal("0")
        assert first.remaining == Decimal("3000")

        second = renewal_service.renew(
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            period_started_at=new_start,
            period_ends_at=new_end,
        )

        assert second.consumed == Decimal("0")
        assert second.remaining == Decimal("3000")

        session.commit()

    finally:
        session.rollback()
        session.close()