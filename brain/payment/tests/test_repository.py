from datetime import datetime, timezone
from decimal import Decimal

from database.database import SessionLocal

from brain.payment.models import Payment, PaymentStatus
from brain.payment.repository import PaymentRepository
from brain.payment.payment_model import PaymentModel
from brain.tier.models import BrainTier


def test_payment_repository_crud():
    user_id = 999979

    session = SessionLocal()

    try:
        session.query(PaymentModel).filter(
            PaymentModel.user_id == user_id
        ).delete()
        session.commit()

        repository = PaymentRepository(session)

        now = datetime.now(timezone.utc)

        payment = Payment(
            payment_id=None,
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            amount=Decimal("499"),
            currency="INR",
            status=PaymentStatus.CREATED,
            provider="razorpay",
            provider_order_id="test_order_999979",
            provider_payment_id="test_payment_999979",
            created_at=now,
            updated_at=now,
        )

        created = repository.create(payment)

        assert created.payment_id is not None
        assert created.user_id == user_id
        assert created.amount == Decimal("499.0000")
        assert created.status == PaymentStatus.CREATED

        fetched = repository.get_by_id(
            created.payment_id
        )

        assert fetched is not None
        assert fetched.payment_id == created.payment_id
        assert fetched.provider_payment_id == (
            "test_payment_999979"
        )

        by_provider = (
            repository.get_by_provider_payment_id(
                "test_payment_999979"
            )
        )

        assert by_provider is not None
        assert by_provider.payment_id == (
            created.payment_id
        )

        user_payments = repository.get_by_user_id(
            user_id
        )

        assert len(user_payments) == 1
        assert user_payments[0].payment_id == (
            created.payment_id
        )

        updated = Payment(
            payment_id=created.payment_id,
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            amount=Decimal("499"),
            currency="INR",
            status=PaymentStatus.SUCCEEDED,
            provider="razorpay",
            provider_order_id="test_order_999979",
            provider_payment_id="test_payment_999979",
            created_at=created.created_at,
            updated_at=datetime.now(timezone.utc),
        )

        saved = repository.update(updated)

        assert saved.status == PaymentStatus.SUCCEEDED

        fetched_again = repository.get_by_id(
            created.payment_id
        )

        assert fetched_again is not None
        assert fetched_again.status == (
            PaymentStatus.SUCCEEDED
        )

    finally:
        session.query(PaymentModel).filter(
            PaymentModel.user_id == user_id
        ).delete()
        session.commit()
        session.close()