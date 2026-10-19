from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

import pytest
from unittest.mock import Mock

from brain.payment.models import Payment, PaymentStatus
from brain.payment.verification_service import PaymentVerificationService
from brain.tier.models import BrainTier


class FakePaymentProvider:
    def __init__(self, verified=True, details_verified=True):
        self.verified = verified
        self.details_verified = details_verified

    def verify_payment(
        self,
        *,
        provider_order_id,
        provider_payment_id,
        signature,
    ):
        return self.verified

    def verify_payment_details(
        self,
        *,
        provider_order_id,
        provider_payment_id,
        expected_amount,
        expected_currency,
    ):
        return self.details_verified


class FakePaymentRepository:
    def __init__(self, payment):
        self.payment = payment
        self.updated_payment = None

    def get_by_id(self, payment_id, *, for_update=False):
        if self.payment.payment_id == payment_id:
            return self.payment
        return None

    def update(self, payment):
        self.updated_payment = payment
        self.payment = payment
        return payment


def make_payment(
    *,
    status=PaymentStatus.CREATED,
    payment_id=123,
    user_id=999978,
    tier=BrainTier.THALAMUS,
):
    now = datetime.now(timezone.utc)

    return Payment(
        payment_id=payment_id,
        user_id=user_id,
        tier=tier,
        amount=Decimal("499"),
        currency="INR",
        status=status,
        provider="razorpay",
        provider_order_id=f"order_test_{payment_id}",
        provider_payment_id=(
            "pay_test_123"
            if status == PaymentStatus.SUCCEEDED
            else None
        ),
        created_at=now,
        updated_at=now,
    )


def make_service(payment):
    repository = FakePaymentRepository(payment)
    provider = FakePaymentProvider()

    activation_service = Mock()
    wallet_operations = Mock()

    service = PaymentVerificationService(
        payment_repository=repository,
        payment_provider=provider,
        subscription_activation_service=activation_service,
        wallet_operations=wallet_operations,
    )

    return (
        service,
        repository,
        provider,
        activation_service,
        wallet_operations,
    )


def test_successful_payment_credits_correct_brain_units():
    payment = make_payment()

    (
        service,
        repository,
        provider,
        activation_service,
        wallet_operations,
    ) = make_service(payment)

    result = service.verify_payment(
        payment_id=payment.payment_id,
        user_id=payment.user_id,
        provider_payment_id="pay_test_123",
        signature="valid_signature",
    )

    assert result.status == PaymentStatus.SUCCEEDED

    wallet_operations.recharge.assert_called_once_with(
        user_id=payment.user_id,
        units=9000,
        reference_id=f"payment:{payment.payment_id}",
        metadata={
            "payment_id": payment.payment_id,
            "tier": payment.tier.value,
        },
    )

    activation_service.activate_from_payment.assert_called_once()


def test_invalid_signature_does_not_update_or_credit():
    payment = make_payment()

    (
        service,
        repository,
        provider,
        activation_service,
        wallet_operations,
    ) = make_service(payment)

    provider.verified = False

    with pytest.raises(
        ValueError,
        match="Payment signature verification failed",
    ):
        service.verify_payment(
            payment_id=payment.payment_id,
            user_id=payment.user_id,
            provider_payment_id="pay_test_123",
            signature="invalid_signature",
        )

    assert repository.updated_payment is None
    activation_service.activate_from_payment.assert_not_called()
    wallet_operations.recharge.assert_not_called()


def test_invalid_payment_details_do_not_credit():
    payment = make_payment()

    (
        service,
        repository,
        provider,
        activation_service,
        wallet_operations,
    ) = make_service(payment)

    provider.details_verified = False

    with pytest.raises(
        ValueError,
        match="Payment amount, currency, order, or capture status is invalid",
    ):
        service.verify_payment(
            payment_id=payment.payment_id,
            user_id=payment.user_id,
            provider_payment_id="pay_test_123",
            signature="valid_signature",
        )

    assert repository.updated_payment is None
    activation_service.activate_from_payment.assert_not_called()
    wallet_operations.recharge.assert_not_called()


def test_successful_payment_retry_uses_same_idempotency_reference():
    payment = make_payment(status=PaymentStatus.SUCCEEDED)

    (
        service,
        repository,
        provider,
        activation_service,
        wallet_operations,
    ) = make_service(payment)
    provider.verify_payment = Mock(
    side_effect=AssertionError(
        "Provider verification must not run for an already-successful payment"
    )
)

    first = service.verify_payment(
        payment_id=payment.payment_id,
        user_id=payment.user_id,
        provider_payment_id="pay_test_123",
        signature="signature",
    )

    second = service.verify_payment(
        payment_id=payment.payment_id,
        user_id=payment.user_id,
        provider_payment_id="pay_test_123",
        signature="signature",
    )

    assert first.status == PaymentStatus.SUCCEEDED
    assert second.status == PaymentStatus.SUCCEEDED

    assert wallet_operations.recharge.call_count == 2

    expected_reference = f"payment:{payment.payment_id}"

    for call in wallet_operations.recharge.call_args_list:
        assert call.kwargs["reference_id"] == expected_reference

    activation_service.activate_from_payment.assert_not_called()
    assert provider.verified is True


def test_distinct_successful_payments_use_distinct_references():
    first_payment = make_payment(
        status=PaymentStatus.SUCCEEDED,
        payment_id=201,
        user_id=999977,
    )

    second_payment = make_payment(
        status=PaymentStatus.SUCCEEDED,
        payment_id=202,
        user_id=999977,
    )

    service, _, _, _, wallet_operations = make_service(first_payment)

    service.verify_payment(
        payment_id=201,
        user_id=first_payment.user_id,
        provider_payment_id="pay_test_201",
        signature="signature",
    )

    service._payment_repository.payment = second_payment

    service.verify_payment(
        payment_id=202,
        user_id=second_payment.user_id,
        provider_payment_id="pay_test_202",
        signature="signature",
    )

    references = [
        call.kwargs["reference_id"]
        for call in wallet_operations.recharge.call_args_list
    ]

    assert references == [
        "payment:201",
        "payment:202",
    ]


def test_payment_cannot_be_verified_by_another_user():
    payment = make_payment()

    (
        service,
        repository,
        provider,
        activation_service,
        wallet_operations,
    ) = make_service(payment)

    with pytest.raises(
        ValueError,
        match="Payment does not belong to the current user",
    ):
        service.verify_payment(
            payment_id=payment.payment_id,
            user_id=123456,
            provider_payment_id="pay_test_123",
            signature="signature",
        )

    assert repository.updated_payment is None
    activation_service.activate_from_payment.assert_not_called()
    wallet_operations.recharge.assert_not_called()