from decimal import Decimal

from sqlalchemy.orm import Session

from brain.recharge.wallet.repository import BrainWalletRepository
from brain.recharge.wallet.transaction_repository import (
    BrainTransactionRepository,
)
from brain.recharge.wallet.service import BrainWalletService
from brain.recharge.wallet.wallet_operations import BrainWalletOperations


class AccountProvisioningService:
    """
    Provisions the initial Brain Wallet for a newly created account.
    """

    INITIAL_FREE_BRAIN_UNITS = Decimal("100")

    def __init__(self, db: Session):
        if db is None:
            raise ValueError("Database session is required.")

        self._wallet_operations = BrainWalletOperations(
            wallet_repository=BrainWalletRepository(db),
            transaction_repository=BrainTransactionRepository(db),
            wallet_service=BrainWalletService(),
        )

    def provision_new_account(self, user_id: int):
        if user_id <= 0:
            raise ValueError("User ID must be greater than zero.")

        existing_wallet = self._wallet_operations._wallet_repository.get(
            user_id
        )

        if existing_wallet is not None:
            return existing_wallet

        return self._wallet_operations.recharge(
            user_id=user_id,
            units=self.INITIAL_FREE_BRAIN_UNITS,
            reference_id=f"account:{user_id}:initial-free-brain",
            metadata={
                "reason": "initial_free_brain_units",
                "units": str(self.INITIAL_FREE_BRAIN_UNITS),
            },
        )