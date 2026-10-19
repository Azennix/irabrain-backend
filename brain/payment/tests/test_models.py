from datetime import datetime, timezone
from decimal import Decimal

import pytest

from brain.payment.models import Payment, PaymentStatus
from brain.tier.models import BrainTier


def make_payment(**overrides):
    now = datetime.now(timezone.utc)

    data = {
        "payment_id": None,
        "user_id": 1,
        "tier": BrainTier.THALAMUS,
        "amount": Decimal("499"),
        "currency": "INR",
        "status": PaymentStatus.CREATED,
        "provider": "razorpay",
        "provider_order_id": "order_test_123",
        "provider_payment_id": None,
        "created_at": now,
        "updated_at": now,
    }

    data.update(overrides)
    return Payment(**data)


def test_payment_creation():
    payment = make_payment()

    assert payment.user_id == 1
    assert payment.tier == BrainTier.THALAMUS
    assert payment.amount == Decimal("499")
    assert payment.currency == "INR"
    assert payment.status == PaymentStatus.CREATED
    assert payment.provider == "razorpay"


def test_payment_requires_positive_user_id():
    with pytest.raises(ValueError, match="User ID must be positive"):
        make_payment(user_id=0)


def test_payment_requires_paid_tier():
    with pytest.raises(ValueError, match="paid Brain Tier"):
        make_payment(tier=BrainTier.FREE)


def test_payment_requires_positive_amount():
    with pytest.raises(
        ValueError,
        match="Payment amount must be positive",
    ):
        make_payment(amount=Decimal("0"))


def test_payment_requires_currency():
    with pytest.raises(
        ValueError,
        match="Payment currency is required",
    ):
        make_payment(currency="")


def test_payment_requires_provider():
    with pytest.raises(
        ValueError,
        match="Payment provider is required",
    ):
        make_payment(provider="")