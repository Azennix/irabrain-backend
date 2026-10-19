from datetime import datetime, timedelta
from decimal import Decimal

from brain.recharge.entitlement.models import FreeBrainEntitlement
from brain.recharge.entitlement.reset_policy import FreeBrainResetPolicy


def test_reset_is_not_due_before_reset_time():
    policy = FreeBrainResetPolicy()

    started_at = datetime(2026, 10, 4, 10, 0, 0)

    entitlement = FreeBrainEntitlement(
        user_id=1001,
        allowance=Decimal("100"),
        consumed=Decimal("40"),
        reset_interval_hours=24,
        period_started_at=started_at,
        next_reset_at=started_at + timedelta(hours=24),
    )

    now = datetime(2026, 10, 5, 9, 59, 59)

    assert policy.is_reset_due(entitlement, now) is False


def test_reset_is_due_at_reset_time():
    policy = FreeBrainResetPolicy()

    started_at = datetime(2026, 10, 4, 10, 0, 0)

    entitlement = FreeBrainEntitlement(
        user_id=1002,
        allowance=Decimal("100"),
        consumed=Decimal("80"),
        reset_interval_hours=24,
        period_started_at=started_at,
        next_reset_at=started_at + timedelta(hours=24),
    )

    now = datetime(2026, 10, 5, 10, 0, 0)

    assert policy.is_reset_due(entitlement, now) is True


def test_reset_restores_free_brain_allowance():
    policy = FreeBrainResetPolicy()

    started_at = datetime(2026, 10, 4, 10, 0, 0)

    entitlement = FreeBrainEntitlement(
        user_id=1003,
        allowance=Decimal("100"),
        consumed=Decimal("75"),
        reset_interval_hours=24,
        period_started_at=started_at,
        next_reset_at=started_at + timedelta(hours=24),
    )

    now = datetime(2026, 10, 5, 10, 0, 0)

    reset_entitlement = policy.reset(
        entitlement=entitlement,
        now=now,
    )

    assert reset_entitlement.user_id == 1003
    assert reset_entitlement.allowance == Decimal("100")
    assert reset_entitlement.consumed == Decimal("0")
    assert reset_entitlement.reset_interval_hours == 24
    assert reset_entitlement.period_started_at == now
    assert reset_entitlement.next_reset_at == now + timedelta(hours=24)


def test_reset_interval_is_configurable():
    policy = FreeBrainResetPolicy()

    started_at = datetime(2026, 10, 4, 10, 0, 0)

    assert policy.calculate_next_reset(
        period_started_at=started_at,
        reset_interval_hours=12,
    ) == datetime(2026, 10, 4, 22, 0, 0)

    assert policy.calculate_next_reset(
        period_started_at=started_at,
        reset_interval_hours=24,
    ) == datetime(2026, 10, 5, 10, 0, 0)


def test_reset_does_not_change_active_entitlement():
    policy = FreeBrainResetPolicy()

    started_at = datetime(2026, 10, 4, 10, 0, 0)

    entitlement = FreeBrainEntitlement(
        user_id=1004,
        allowance=Decimal("100"),
        consumed=Decimal("25"),
        reset_interval_hours=12,
        period_started_at=started_at,
        next_reset_at=started_at + timedelta(hours=12),
    )

    now = datetime(2026, 10, 4, 18, 0, 0)

    result = policy.reset(
        entitlement=entitlement,
        now=now,
    )

    assert result == entitlement