from datetime import datetime
from decimal import Decimal

from brain.recharge.wallet.transactions import (
    BrainTransaction,
    BrainTransactionType,
)


def test_brain_transaction_creation():
    transaction = BrainTransaction(
        transaction_id="txn-001",
        user_id=1,
        transaction_type=BrainTransactionType.RECHARGE,
        units=Decimal("100"),
        reference_id="payment-001",
        status="completed",
        created_at=datetime.utcnow(),
    )

    assert transaction.transaction_id == "txn-001"
    assert transaction.user_id == 1
    assert transaction.transaction_type == BrainTransactionType.RECHARGE
    assert transaction.units == Decimal("100")
    assert transaction.reference_id == "payment-001"
    assert transaction.status == "completed"


def test_transaction_types():
    assert BrainTransactionType.RECHARGE.value == "recharge"
    assert BrainTransactionType.TASK_CONSUMPTION.value == "task_consumption"
    assert BrainTransactionType.REFUND.value == "refund"
    assert BrainTransactionType.PROMOTIONAL_CREDIT.value == "promotional_credit"
    assert BrainTransactionType.ADJUSTMENT.value == "adjustment"
    assert BrainTransactionType.EXPIRATION.value == "expiration"


def test_transaction_metadata():
    transaction = BrainTransaction(
        transaction_id="txn-002",
        user_id=1,
        transaction_type=BrainTransactionType.TASK_CONSUMPTION,
        units=Decimal("8"),
        reference_id="request-001",
        status="completed",
        created_at=datetime.utcnow(),
        metadata={
            "capability": "chat",
            "calculation_version": "v1",
        },
    )

    assert transaction.metadata["capability"] == "chat"
    assert transaction.metadata["calculation_version"] == "v1"