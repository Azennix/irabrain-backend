from datetime import datetime
from decimal import Decimal

from brain.recharge.wallet.transaction_repository import (
    BrainTransactionRepository,
)
from brain.recharge.wallet.transactions import (
    BrainTransaction,
    BrainTransactionStatus,
    BrainTransactionType,
)
from database.database import SessionLocal


def test_create_brain_transaction():
    session = SessionLocal()

    try:
        repository = BrainTransactionRepository(session)

        transaction = BrainTransaction(
            transaction_id="test-txn-repository-001",
            user_id=999999,
            transaction_type=BrainTransactionType.RECHARGE,
            units=Decimal("100"),
            reference_id="test-payment-001",
            status=BrainTransactionStatus.COMPLETED,
            created_at=datetime.utcnow(),
            metadata={
                "source": "repository_test",
                "calculation_version": "v1",
            },
        )

        saved = repository.create(transaction)

        assert saved.transaction_id == transaction.transaction_id
        assert saved.user_id == 999999
        assert saved.transaction_type == BrainTransactionType.RECHARGE
        assert saved.units == Decimal("100")
        assert saved.reference_id == "test-payment-001"
        assert saved.status == BrainTransactionStatus.COMPLETED
        assert saved.metadata["source"] == "repository_test"
        assert saved.metadata["calculation_version"] == "v1"

        session.rollback()

    finally:
        session.close()



def test_get_transaction_by_reference_id():
    session = SessionLocal()

    try:
        repository = BrainTransactionRepository(session)

        transaction = BrainTransaction(
            transaction_id="test-reference-lookup-001",
            user_id=999994,
            transaction_type=BrainTransactionType.RECHARGE,
            units=Decimal("100"),
            reference_id="razorpay-reference-test-001",
            status=BrainTransactionStatus.COMPLETED,
            created_at=datetime.utcnow(),
            metadata={
                "source": "reference_lookup_test",
            },
        )

        repository.create(transaction)

        found = repository.get_by_reference_id(
            "razorpay-reference-test-001"
        )

        assert found is not None
        assert found.transaction_id == "test-reference-lookup-001"
        assert found.user_id == 999994
        assert found.transaction_type == BrainTransactionType.RECHARGE
        assert found.units == Decimal("100")
        assert found.reference_id == "razorpay-reference-test-001"
        assert found.status == BrainTransactionStatus.COMPLETED
        assert found.metadata["source"] == "reference_lookup_test"

        missing = repository.get_by_reference_id(
            "reference-that-does-not-exist"
        )

        assert missing is None

        session.rollback()

    finally:
        session.close()