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

    Free Brain entitlement is managed separately.
    The paid wallet must start with zero balance.
    """

    def __init__(self, db: Session):
        if db is None:
            raise ValueError("Database session is required.")

        self._wallet_operations = BrainWalletOperations(
            wallet_repository=BrainWalletRepository(db),
            transaction_repository=BrainTransactionRepository(db),
            wallet_service=BrainWalletService(),
        )

    def provision_new_account(self, user_id: int):
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be greater than zero.")

        return self._wallet_operations.get_or_create_wallet(user_id)