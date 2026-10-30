from datetime import datetime, timezone
from decimal import Decimal

from brain.recharge.wallet.repository import BrainWalletRepository
from brain.recharge.entitlement.service import FreeBrainEntitlementService
from brain.recharge.config import DEV_BRAIN_RECHARGE_CONFIG


class BrainBalanceService:
    def __init__(
        self,
        wallet_repository: BrainWalletRepository,
        free_brain_service: FreeBrainEntitlementService,
    ):
        if wallet_repository is None:
            raise ValueError("Wallet repository is required.")

        if free_brain_service is None:
            raise ValueError("Free Brain entitlement service is required.")

        self._wallet_repository = wallet_repository
        self._free_brain_service = free_brain_service

    def get_balance(self, user_id: int) -> dict:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be greater than zero.")

        now = datetime.now(timezone.utc)

        # Refresh the existing Free Brain entitlement.
        # The entitlement service applies a reset when it is due.
        free_cfg = DEV_BRAIN_RECHARGE_CONFIG.free_brain

        entitlement = self._free_brain_service.get_or_create(
            user_id=user_id,
            allowance=free_cfg.allowance,
            reset_interval_hours=free_cfg.reset_interval_hours,
            now=now,
        )
        self._free_brain_service.commit()

        included_balance = Decimal("0")

        if entitlement is not None:
            included_balance = max(
                Decimal("0"),
                Decimal(str(entitlement.allowance))
                - Decimal(str(entitlement.consumed)),
            )

        # Paid Brain balance remains separate.
        wallet = self._wallet_repository.get(user_id)

        paid_balance = (
            Decimal(str(wallet.current_balance))
            if wallet is not None
            else Decimal("0")
        )

        total_balance = included_balance + paid_balance

        return {
            "user_id": user_id,
            "included_balance": included_balance,
            "paid_balance": paid_balance,
            "total_balance": total_balance,
        }
