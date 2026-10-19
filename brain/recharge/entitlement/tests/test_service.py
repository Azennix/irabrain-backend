from datetime import datetime
from decimal import Decimal

from brain.recharge.entitlement.models import FreeBrainEntitlement
from brain.recharge.entitlement.repository import (
    FreeBrainEntitlementRepository,
)
from brain.recharge.entitlement.reset_policy import (
    FreeBrainResetPolicy,
)
from brain.recharge.entitlement.service import (
    FreeBrainEntitlementService,
)
from database.database import SessionLocal
from brain.recharge.entitlement.consumption import (
    FreeBrainConsumptionPolicy,
)

def build_service(session):
    repository = FreeBrainEntitlementRepository(session)
    reset_policy = FreeBrainResetPolicy()
    consumption_policy = FreeBrainConsumptionPolicy()

    return FreeBrainEntitlementService(
        repository=repository,
        reset_policy=reset_policy,
        consumption_policy=consumption_policy,
    )


def test_get_or_create_creates_free_entitlement():
    session = SessionLocal()

    try:
        service = build_service(session)

        now = datetime(2026, 10, 4, 10, 0, 0)

        entitlement = service.get_or_create(
            user_id=999978,
            allowance=Decimal("100"),
            reset_interval_hours=24,
            now=now,
        )

        assert entitlement.user_id == 999978
        assert entitlement.allowance == Decimal("100")
        assert entitlement.consumed == Decimal("0")
        assert entitlement.reset_interval_hours == 24
        assert entitlement.period_started_at == now
        assert entitlement.next_reset_at == datetime(
            2026, 10, 5, 10, 0, 0
        )

        session.rollback()

    finally:
        session.close()


def test_get_or_create_returns_existing_entitlement():
    session = SessionLocal()

    try:
        service = build_service(session)

        first_time = datetime(2026, 10, 4, 10, 0, 0)

        first = service.get_or_create(
            user_id=999977,
            allowance=Decimal("100"),
            reset_interval_hours=24,
            now=first_time,
        )

        second = service.get_or_create(
            user_id=999977,
            allowance=Decimal("500"),
            reset_interval_hours=12,
            now=datetime(2026, 10, 4, 15, 0, 0),
        )

        assert second.user_id == first.user_id
        assert second.allowance == Decimal("100")
        assert second.reset_interval_hours == 24
        assert second.period_started_at == first_time

        session.rollback()

    finally:
        session.close()


def test_refresh_resets_due_entitlement():
    session = SessionLocal()

    try:
        service = build_service(session)

        started_at = datetime(2026, 10, 4, 10, 0, 0)

        service.get_or_create(
            user_id=999976,
            allowance=Decimal("100"),
            reset_interval_hours=24,
            now=started_at,
        )

        repository = FreeBrainEntitlementRepository(session)

        stored = repository.get(999976)

        assert stored is not None

        consumed_entitlement = FreeBrainEntitlement(
            user_id=stored.user_id,
            allowance=stored.allowance,
            consumed=Decimal("75"),
            reset_interval_hours=stored.reset_interval_hours,
            period_started_at=stored.period_started_at,
            next_reset_at=stored.next_reset_at,
        )

        repository.update(consumed_entitlement)

        refreshed = service.refresh(
            user_id=999976,
            now=datetime(2026, 10, 5, 10, 0, 0),
        )

        assert refreshed.allowance == Decimal("100")
        assert refreshed.consumed == Decimal("0")
        assert refreshed.period_started_at == datetime(
            2026, 10, 5, 10, 0, 0
        )
        assert refreshed.next_reset_at == datetime(
            2026, 10, 6, 10, 0, 0
        )

        session.rollback()

    finally:
        session.close()


def test_refresh_does_not_reset_before_due_time():
    session = SessionLocal()

    try:
        service = build_service(session)

        started_at = datetime(2026, 10, 4, 10, 0, 0)

        service.get_or_create(
            user_id=999975,
            allowance=Decimal("100"),
            reset_interval_hours=24,
            now=started_at,
        )

        repository = FreeBrainEntitlementRepository(session)

        stored = repository.get(999975)

        assert stored is not None

        consumed_entitlement = FreeBrainEntitlement(
            user_id=stored.user_id,
            allowance=stored.allowance,
            consumed=Decimal("60"),
            reset_interval_hours=stored.reset_interval_hours,
            period_started_at=stored.period_started_at,
            next_reset_at=stored.next_reset_at,
        )

        repository.update(consumed_entitlement)

        refreshed = service.refresh(
            user_id=999975,
            now=datetime(2026, 10, 5, 9, 59, 59),
        )

        assert refreshed.consumed == Decimal("60")
        assert refreshed.period_started_at == started_at
        assert refreshed.next_reset_at == datetime(
            2026, 10, 5, 10, 0, 0
        )

        session.rollback()

    finally:
        session.close()

def test_consume_persists_free_brain_usage():
    session = SessionLocal()

    try:
        service = build_service(session)

        now = datetime(2026, 10, 4, 10, 0, 0)

        service.get_or_create(
            user_id=999974,
            allowance=Decimal("100"),
            reset_interval_hours=24,
            now=now,
        )

        entitlement, consumed, fully_consumed = service.consume(
            user_id=999974,
            requested_units=Decimal("30"),
            now=datetime(2026, 10, 4, 11, 0, 0),
        )

        assert entitlement.consumed == Decimal("30")
        assert consumed == Decimal("30")
        assert fully_consumed is True

        repository = FreeBrainEntitlementRepository(session)
        stored = repository.get(999974)

        assert stored is not None
        assert stored.consumed == Decimal("30")

        session.rollback()

    finally:
        session.close()


def test_consume_only_uses_remaining_free_brain():
    session = SessionLocal()

    try:
        service = build_service(session)

        now = datetime(2026, 10, 4, 10, 0, 0)

        service.get_or_create(
            user_id=999973,
            allowance=Decimal("100"),
            reset_interval_hours=24,
            now=now,
        )

        service.consume(
            user_id=999973,
            requested_units=Decimal("80"),
            now=datetime(2026, 10, 4, 11, 0, 0),
        )

        entitlement, consumed, fully_consumed = service.consume(
            user_id=999973,
            requested_units=Decimal("50"),
            now=datetime(2026, 10, 4, 12, 0, 0),
        )

        assert entitlement.consumed == Decimal("100")
        assert consumed == Decimal("20")
        assert fully_consumed is False

        session.rollback()

    finally:
        session.close()


def test_consume_resets_free_brain_before_consumption_when_due():
    session = SessionLocal()

    try:
        service = build_service(session)

        started_at = datetime(2026, 10, 4, 10, 0, 0)

        service.get_or_create(
            user_id=999972,
            allowance=Decimal("100"),
            reset_interval_hours=24,
            now=started_at,
        )

        service.consume(
            user_id=999972,
            requested_units=Decimal("90"),
            now=datetime(2026, 10, 4, 12, 0, 0),
        )

        entitlement, consumed, fully_consumed = service.consume(
            user_id=999972,
            requested_units=Decimal("40"),
            now=datetime(2026, 10, 5, 10, 0, 0),
        )

        assert entitlement.consumed == Decimal("40")
        assert consumed == Decimal("40")
        assert fully_consumed is True
        assert entitlement.period_started_at == datetime(
            2026, 10, 5, 10, 0, 0
        )

        session.rollback()

    finally:
        session.close()