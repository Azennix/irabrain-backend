from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4

from brain.recharge.wallet.transactions import (
    BrainTransaction,
    BrainTransactionStatus,
    BrainTransactionType,
)

from brain.recharge.wallet.models import BrainWallet
from brain.recharge.wallet.repository import BrainWalletRepository
from brain.recharge.wallet.service import BrainWalletService
from brain.recharge.wallet.transaction_repository import (
    BrainTransactionRepository,
)


class BrainWalletOperations:
    def __init__(
        self,
        wallet_repository: BrainWalletRepository,
        transaction_repository: BrainTransactionRepository,
        wallet_service: BrainWalletService,
    ):
        if wallet_repository is None:
            raise ValueError("Wallet repository is required.")

        if transaction_repository is None:
            raise ValueError("Transaction repository is required.")

        if wallet_service is None:
            raise ValueError("Wallet service is required.")

        self._wallet_repository = wallet_repository
        self._transaction_repository = transaction_repository
        self._wallet_service = wallet_service

    def get_or_create_wallet(self, user_id: int) -> BrainWallet:

        wallet = self._wallet_repository.get(user_id)

        if wallet is not None:
            return wallet

        return self._wallet_repository.create(user_id)


    def recharge(
        self,
        user_id: int,
        units: Decimal,
        reference_id: str | None = None,
        metadata: dict | None = None,
    ) -> BrainWallet:


        if user_id <= 0:
            raise ValueError("User ID must be greater than zero.")

        if units <= Decimal("0"):
            raise ValueError("Recharge Brain Units must be positive.")

        if reference_id is not None and not reference_id.strip():
            raise ValueError("Reference ID cannot be empty.")




        if reference_id:
            existing_transaction = (
                self._transaction_repository.get_by_reference_id(
                    reference_id
            )
        )

            if existing_transaction is not None:
                if (
                    existing_transaction.transaction_type
                    != BrainTransactionType.RECHARGE
      ):
                    raise ValueError(
                        "Reference ID is already associated with "
                        "a different transaction type."
        )

                if existing_transaction.user_id != user_id:
                    raise ValueError(
                        "Reference ID belongs to a different user."
        )

                if existing_transaction.units != units:
                    raise ValueError(
                       "Reference ID was already used with a different "
                       "Brain Units amount."
    )

                wallet = self._wallet_repository.get(user_id)

                if wallet is None:
                    raise ValueError(
                       "Brain wallet does not exist."
        )

                return wallet




        wallet = self.get_or_create_wallet(user_id)

        updated_wallet = self._wallet_service.recharge(
            wallet,
            units,
    )

        transaction = BrainTransaction(
            transaction_id=str(uuid4()),
            user_id=user_id,
            transaction_type=BrainTransactionType.RECHARGE,
            units=units,
            reference_id=reference_id,
            status=BrainTransactionStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
            metadata=metadata or {},
    )

        self._transaction_repository.create(transaction)
        self._wallet_repository.update(updated_wallet)

        return updated_wallet

    def consume(
        self,
        user_id: int,
        units: Decimal,
        reference_id: str | None = None,
        metadata: dict | None = None,
    ) -> BrainWallet:
        if user_id <= 0:
            raise ValueError("User ID must be greater than zero.")

        if units <= Decimal("0"):
            raise ValueError("Consumed Brain Units must be positive.")

        if reference_id:
            existing_transaction = (
                self._transaction_repository.get_by_reference_id(
                    reference_id
            )
        )

            if existing_transaction is not None:
                if (
                    existing_transaction.transaction_type
                    != BrainTransactionType.TASK_CONSUMPTION
            ):
                    raise ValueError(
                        "Reference ID is already associated with "
                        "a different transaction type."
                )

                if existing_transaction.user_id != user_id:
                    raise ValueError(
                        "Reference ID belongs to a different user."
                )
                if existing_transaction.units != units:
                    raise ValueError(
                        "Reference ID was already used with a different "
                        "Brain Units amount."
                )

                wallet = self._wallet_repository.get(user_id)

                if wallet is None:
                    raise ValueError("Brain wallet does not exist.")

                return wallet

        wallet = self.get_or_create_wallet(user_id)



        updated_wallet = self._wallet_service.consume(
            wallet,
            units,
    )

        transaction = BrainTransaction(
            transaction_id=str(uuid4()),
            user_id=user_id,
            transaction_type=BrainTransactionType.TASK_CONSUMPTION,
            units=units,
            reference_id=reference_id,
            status=BrainTransactionStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
            metadata=metadata or {},
    )

        self._transaction_repository.create(transaction)
        self._wallet_repository.update(updated_wallet)

        return updated_wallet

    def get_transaction_by_reference_id(
        self,
        reference_id: str,
):
        if not reference_id:
            raise ValueError("Reference ID is required.")

        return self._transaction_repository.get_by_reference_id(
            reference_id
    )