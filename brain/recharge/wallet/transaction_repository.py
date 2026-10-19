import json
from decimal import Decimal

from sqlalchemy.orm import Session

from brain.recharge.wallet.brain_transaction_model import (
    BrainTransactionModel,
)
from brain.recharge.wallet.transactions import (
    BrainTransaction,
    BrainTransactionStatus,
    BrainTransactionType,
)


class BrainTransactionRepository:
    def __init__(self, session: Session):
        if session is None:
            raise ValueError("Database session is required.")

        self._session = session

    def create(
        self,
        transaction: BrainTransaction,
    ) -> BrainTransaction:
        if transaction is None:
            raise ValueError("Brain transaction is required.")

        model = BrainTransactionModel(
            transaction_id=transaction.transaction_id,
            user_id=transaction.user_id,
            transaction_type=transaction.transaction_type.value,
            units=transaction.units,
            reference_id=transaction.reference_id,
            status=transaction.status.value,
            metadata_json=(
                json.dumps(transaction.metadata)
                if transaction.metadata
                else None
            ),
            created_at=transaction.created_at,
        )

        self._session.add(model)
        self._session.flush()

        return BrainTransaction(
            transaction_id=model.transaction_id,
            user_id=model.user_id,
            transaction_type=BrainTransactionType(
                model.transaction_type
            ),
            units=Decimal(model.units),
            reference_id=model.reference_id,
            status=BrainTransactionStatus(model.status),
            created_at=model.created_at,
            metadata=(
                json.loads(model.metadata_json)
                if model.metadata_json
                else {}
            ),
        )


    def get_by_reference_id(
        self,
        reference_id: str,
    ) -> BrainTransaction | None:
        if not reference_id:
            raise ValueError("Reference ID is required.")

        model = (
            self._session.query(BrainTransactionModel)
            .filter(
                BrainTransactionModel.reference_id == reference_id
        )
            .first()
    )

        if model is None:
            return None

        return BrainTransaction(
            transaction_id=model.transaction_id,
            user_id=model.user_id,
            transaction_type=BrainTransactionType(
                model.transaction_type
        ),
            units=Decimal(model.units),
            reference_id=model.reference_id,
            status=BrainTransactionStatus(model.status),
            created_at=model.created_at,
            metadata=(
                json.loads(model.metadata_json)
                if model.metadata_json
                else {}
        ),
    )
