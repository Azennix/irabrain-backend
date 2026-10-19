from datetime import datetime
from decimal import Decimal

from brain.recharge.entitlement.models import FreeBrainEntitlement
from brain.recharge.entitlement.repository import (
    FreeBrainEntitlementRepository,
)
from database.database import SessionLocal


def test_create_and_get_free_brain_entitlement():
    session = SessionLocal()

    try:
        repository = FreeBrainEntitlementRepository(session)

        user_id = 999980
        started_at = datetime(2026, 10, 4, 10, 0, 0)
        next_reset_at = datetime(2026, 10, 5, 10, 0, 0)

        entitlement = FreeBrainEntitlement(
            user_id=user_id,
            allowance=Decimal("100"),
            consumed=Decimal("25"),
            reset_interval_hours=24,
            period_started_at=started_at,
            next_reset_at=next_reset_at,
        )

        repository.create(entitlement)

        stored = repository.get(user_id)

        assert stored is not None
        assert stored.user_id == user_id
        assert stored.allowance == Decimal("100")
        assert stored.consumed == Decimal("25")
        assert stored.reset_interval_hours == 24
        assert stored.period_started_at == started_at
        assert stored.next_reset_at == next_reset_at

        session.rollback()

    finally:
        session.close()


def test_update_free_brain_entitlement():
    session = SessionLocal()

    try:
        repository = FreeBrainEntitlementRepository(session)

        user_id = 999979
        started_at = datetime(2026, 10, 4, 10, 0, 0)
        next_reset_at = datetime(2026, 10, 5, 10, 0, 0)

        entitlement = FreeBrainEntitlement(
            user_id=user_id,
            allowance=Decimal("100"),
            consumed=Decimal("40"),
            reset_interval_hours=24,
            period_started_at=started_at,
            next_reset_at=next_reset_at,
        )

        repository.create(entitlement)

        updated = FreeBrainEntitlement(
            user_id=user_id,
            allowance=Decimal("100"),
            consumed=Decimal("0"),
            reset_interval_hours=12,
            period_started_at=datetime(2026, 10, 5, 10, 0, 0),
            next_reset_at=datetime(2026, 10, 5, 22, 0, 0),
        )

        repository.update(updated)

        stored = repository.get(user_id)

        assert stored is not None
        assert stored.allowance == Decimal("100")
        assert stored.consumed == Decimal("0")
        assert stored.reset_interval_hours == 12
        assert stored.period_started_at == datetime(
            2026, 10, 5, 10, 0, 0
        )
        assert stored.next_reset_at == datetime(
            2026, 10, 5, 22, 0, 0
        )

        session.rollback()

    finally:
        session.close()