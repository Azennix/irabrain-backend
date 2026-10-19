from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import DATABASE_URL
from brain.payment.models import Payment, PaymentStatus
from brain.payment.payment_model import PaymentModel
from brain.payment.repository import PaymentRepository
from brain.payment.verification_service import PaymentVerificationService
from brain.recharge.wallet.repository import BrainWalletRepository
from brain.recharge.wallet.service import BrainWalletService
from brain.recharge.wallet.transaction_repository import BrainTransactionRepository
from brain.recharge.wallet.wallet_operations import BrainWalletOperations
from brain.tier.models import BrainTier


@pytest.fixture
def db_session():
    from sqlalchemy.engine import make_url

    url = make_url(DATABASE_URL)

    if url.database != "irabrain_test":
        pytest.fail(
            f"Refusing to run integration test against {url.database!r}"
        )

    engine = create_engine(url)
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()


class ValidProvider:
    def verify_payment(self, **kwargs):
        return True

    def verify_payment_details(self, **kwargs):
        return True


def test_payment_status_rolls_back_when_wallet_credit_fails(db_session):
    user_id = 888001
    now = datetime.now(timezone.utc)

    payment_model = PaymentModel(
        user_id=user_id,
        tier=BrainTier.THALAMUS.value,
        amount=Decimal("499"),
        currency="INR",
        status=PaymentStatus.CREATED.value,
        provider="test",
        provider_order_id="order_rollback_integration_888001",
        provider_payment_id=None,
        created_at=now,
        updated_at=now,
    )

    db_session.add(payment_model)
    db_session.flush()
    payment_id = payment_model.payment_id

    payment_repository = PaymentRepository(db_session)

    wallet_operations = Mock()
    wallet_operations.recharge.side_effect = RuntimeError(
        "Intentional integration-test wallet failure"
    )

    service = PaymentVerificationService(
        payment_repository=payment_repository,
        payment_provider=ValidProvider(),
        subscription_activation_service=Mock(),
        wallet_operations=wallet_operations,
    )

    try:
        with pytest.raises(
            RuntimeError,
            match="Intentional integration-test wallet failure",
        ):
            service.verify_payment(
                payment_id=payment_id,
                user_id=user_id,
                provider_payment_id="pay_rollback_integration_888001",
                signature="valid-test-signature",
            )

        db_session.rollback()

        persisted_payment = payment_repository.get_by_id(payment_id)

        assert persisted_payment is not None
        assert persisted_payment.status == PaymentStatus.CREATED
        assert persisted_payment.provider_payment_id is None

    finally:
        db_session.rollback()
        db_session.query(PaymentModel).filter(
            PaymentModel.payment_id == payment_id
        ).delete(synchronize_session=False)
        db_session.commit()
