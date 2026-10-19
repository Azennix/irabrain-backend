from datetime import datetime, timezone
from decimal import Decimal

from brain.payment.models import Payment, PaymentStatus
from brain.payment.providers.base import PaymentOrder
from brain.payment.service import PaymentService
from brain.tier.models import BrainTier


class FakePaymentProvider:

    def create_order(
        self,
        *,
        user_id,
        tier,
        amount,
        currency,
    ):
        return PaymentOrder(
            provider="razorpay",
            provider_order_id="order_test_123",
            user_id=user_id,
            tier=tier,
            amount=amount,
            currency=currency,
        )


class FakePaymentRepository:

    def __init__(self):
        self.created_payment = None

    def create(self, payment):
        self.created_payment = Payment(
            payment_id=123,
            user_id=payment.user_id,
            tier=payment.tier,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            provider=payment.provider,
            provider_order_id=payment.provider_order_id,
            provider_payment_id=payment.provider_payment_id,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )
        return self.created_payment


def test_payment_service_creates_payment():

    repository = FakePaymentRepository()
    provider = FakePaymentProvider()

    service = PaymentService(
        payment_repository=repository,
        payment_provider=provider,
    )

    payment = service.create_payment(
        user_id=999979,
        tier=BrainTier.THALAMUS,
        amount=Decimal("499"),
        currency="INR",
    )

    assert payment.payment_id == 123
    assert payment.user_id == 999979
    assert payment.tier == BrainTier.THALAMUS
    assert payment.amount == Decimal("499")
    assert payment.currency == "INR"
    assert payment.status == PaymentStatus.CREATED
    assert payment.provider == "razorpay"
    assert payment.provider_order_id == "order_test_123"
    assert payment.provider_payment_id is None