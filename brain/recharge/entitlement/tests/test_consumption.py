from decimal import Decimal

from brain.recharge.entitlement.consumption import (
    FreeBrainConsumptionPolicy,
)
from brain.recharge.entitlement.models import FreeBrainEntitlement


def build_entitlement(
    allowance: str,
    consumed: str,
) -> FreeBrainEntitlement:
    return FreeBrainEntitlement(
        user_id=1001,
        allowance=Decimal(allowance),
        consumed=Decimal(consumed),
        reset_interval_hours=24,
        period_started_at=None,
        next_reset_at=None,
    )


def test_consumes_from_available_free_brain():
    policy = FreeBrainConsumptionPolicy()

    entitlement = build_entitlement(
        allowance="100",
        consumed="40",
    )

    result = policy.calculate(
        entitlement=entitlement,
        requested_units=Decimal("20"),
    )

    assert result.consumed == Decimal("20")
    assert result.remaining == Decimal("40")
    assert result.fully_consumed is True


def test_consumes_only_remaining_free_brain():
    policy = FreeBrainConsumptionPolicy()

    entitlement = build_entitlement(
        allowance="100",
        consumed="90",
    )

    result = policy.calculate(
        entitlement=entitlement,
        requested_units=Decimal("30"),
    )

    assert result.consumed == Decimal("10")
    assert result.remaining == Decimal("0")
    assert result.fully_consumed is False


def test_zero_remaining_free_brain_consumes_nothing():
    policy = FreeBrainConsumptionPolicy()

    entitlement = build_entitlement(
        allowance="100",
        consumed="100",
    )

    result = policy.calculate(
        entitlement=entitlement,
        requested_units=Decimal("10"),
    )

    assert result.consumed == Decimal("0")
    assert result.remaining == Decimal("0")
    assert result.fully_consumed is False


def test_rejects_non_positive_request():
    policy = FreeBrainConsumptionPolicy()

    entitlement = build_entitlement(
        allowance="100",
        consumed="20",
    )

    try:
        policy.calculate(
            entitlement=entitlement,
            requested_units=Decimal("0"),
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "greater than zero" in str(exc)


def test_rejects_invalid_free_balance():
    policy = FreeBrainConsumptionPolicy()

    entitlement = build_entitlement(
        allowance="100",
        consumed="120",
    )

    try:
        policy.calculate(
            entitlement=entitlement,
            requested_units=Decimal("10"),
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "invalid balance" in str(exc)