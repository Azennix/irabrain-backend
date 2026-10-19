from datetime import datetime, timezone
from decimal import Decimal

from brain.recharge.wallet.models import BrainWallet


class BrainWalletService:

    def consume(
        self,
        wallet: BrainWallet,
        units: Decimal,
        timestamp: datetime | None = None,
    ) -> BrainWallet:
        if wallet is None:
            raise ValueError("Brain wallet is required.")

        if units <= Decimal("0"):
            raise ValueError("Consumed Brain Units must be greater than zero.")

        if units > wallet.current_balance:
            raise ValueError("Insufficient Brain Balance.")

        updated_at = timestamp or datetime.now(timezone.utc)

        return BrainWallet(
            user_id=wallet.user_id,
            current_balance=wallet.current_balance - units,
            lifetime_purchased=wallet.lifetime_purchased,
            lifetime_consumed=wallet.lifetime_consumed + units,
            updated_at=updated_at,
        )

    def recharge(
        self,
        wallet: BrainWallet,
        units: Decimal,
        timestamp: datetime | None = None,
    ) -> BrainWallet:
        if wallet is None:
            raise ValueError("Brain wallet is required.")

        if units <= Decimal("0"):
            raise ValueError("Recharge Brain Units must be greater than zero.")

        updated_at = timestamp or datetime.now(timezone.utc)

        return BrainWallet(
            user_id=wallet.user_id,
            current_balance=wallet.current_balance + units,
            lifetime_purchased=wallet.lifetime_purchased + units,
            lifetime_consumed=wallet.lifetime_consumed,
            updated_at=updated_at,
        )