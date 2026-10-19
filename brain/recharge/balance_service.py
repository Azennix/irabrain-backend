from decimal import Decimal

from brain.recharge.wallet.repository import BrainWalletRepository


class BrainBalanceService:
    def __init__(
        self,
        wallet_repository: BrainWalletRepository,
    ):
        if wallet_repository is None:
            raise ValueError("Wallet repository is required.")

        self._wallet_repository = wallet_repository

    def get_balance(self, user_id: int) -> dict:
        wallet = self._wallet_repository.get(user_id)

        balance = (
            Decimal(str(wallet.current_balance))
            if wallet is not None
            else Decimal("0")
        )

        return {
            "user_id": user_id,
            "included_balance": "0",
            "paid_balance": str(balance),
            "total_balance": str(balance),
        }