from datetime import datetime, timezone
from decimal import Decimal

import pytest

from brain.payment.models import Payment, PaymentStatus
from brain.payment.subscription_activation import (
    PaymentSubscriptionActivationService,
)
from brain.tier.models import BrainTier


class FakeSubscriptionActivationService:

    def __init__(self):
        self.called_with = None

    def activate(
        self,
        *,
        user_id,
        tier,
        started_at,
        billing_period_started_at,
        billing_period_ends_at,
    ):
        self.called_with = {
            "user_id": user_id,
            "tier": tier,
            "started_at": started_at,
            "billing_period_started_at": billing_period_started_at,
            "billing_period_ends_at": billing_period_ends_at,
        }

        return "subscription_activated"


def make_payment(status):
    now = datetime.now(timezone.utc)

    return Payment(
        payment_id=123,
        user_id=999979,
        tier=BrainTier.THALAMUS,
        amount=Decimal("499"),
        currency="INR",
        status=status,
        provider="razorpay",
        provider_order_id="order_test_123",
        provider_payment_id="pay_test_123",
        created_at=now,
        updated_at=now,
    )


def test_successful_payment_activates_subscription():

    subscription_service = FakeSubscriptionActivationService()

    service = PaymentSubscriptionActivationService(
        subscription_activation_service=subscription_service,
    )

    started_at = datetime(2026, 10, 9, tzinfo=timezone.utc)
    ends_at = datetime(2026, 11, 9, tzinfo=timezone.utc)

    result = service.activate_from_payment(
        payment=make_payment(PaymentStatus.SUCCEEDED),
        billing_period_started_at=started_at,
        billing_period_ends_at=ends_at,
    )

    assert result == "subscription_activated"
    assert subscription_service.called_with["user_id"] == 999979
    assert (
        subscription_service.called_with["tier"]
        == BrainTier.THALAMUS
    )
    assert (
        subscription_service.called_with["billing_period_started_at"]
        == started_at
    )
    assert (
        subscription_service.called_with["billing_period_ends_at"]
        == ends_at
    )


def test_unsuccessful_payment_cannot_activate_subscription():

    subscription_service = FakeSubscriptionActivationService()

    service = PaymentSubscriptionActivationService(
        subscription_activation_service=subscription_service,
    )

    started_at = datetime(2026, 10, 9, tzinfo=timezone.utc)
    ends_at = datetime(2026, 11, 9, tzinfo=timezone.utc)

    with pytest.raises(
        ValueError,
        match="successful payment",
    ):
        service.activate_from_payment(
            payment=make_payment(PaymentStatus.CREATED),
            billing_period_started_at=started_at,
            billing_period_ends_at=ends_at,
        )

    assert subscription_service.called_with is None