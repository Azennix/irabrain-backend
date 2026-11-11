from datetime import datetime, timezone
from decimal import Decimal

from brain.recharge.wallet.repository import BrainWalletRepository
from brain.recharge.entitlement.service import FreeBrainEntitlementService
from brain.recharge.config import DEV_BRAIN_RECHARGE_CONFIG

from brain.tier.capacity.repository import TierBrainCapacityRepository
from database.user_repository import UserRepository
from brain.tier.models import BrainTier


class BrainBalanceService:

    def __init__(
        self,
        wallet_repository: BrainWalletRepository,
        free_brain_service: FreeBrainEntitlementService,
        user_repository: UserRepository,
        tier_capacity_repository: TierBrainCapacityRepository,
    ):

        if wallet_repository is None:
            raise ValueError("Wallet repository is required.")

        if free_brain_service is None:
            raise ValueError("Free Brain entitlement service is required.")

        if user_repository is None:
            raise ValueError("User repository is required.")

        if tier_capacity_repository is None:
            raise ValueError("Tier capacity repository is required.")

        self._wallet_repository = wallet_repository
        self._free_brain_service = free_brain_service
        self._user_repository = user_repository
        self._tier_capacity_repository = tier_capacity_repository

    def get_balance(self, user_id: int) -> dict:

        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be greater than zero.")

        now = datetime.now(timezone.utc)

        brain_tier = BrainTier(
            self._user_repository.get_brain_tier(user_id)
        )

        included_balance = Decimal("0")
        next_reset_at = None
        reset_interval_hours = None

        if brain_tier == BrainTier.FREE:

            free_cfg = DEV_BRAIN_RECHARGE_CONFIG.free_brain

            entitlement = self._free_brain_service.get_or_create(
                user_id=user_id,
                allowance=free_cfg.allowance,
                reset_interval_hours=free_cfg.reset_interval_hours,
                now=now,
            )

            self._free_brain_service.commit()

            if entitlement is not None:

                included_balance = max(
                    Decimal("0"),
                    Decimal(str(entitlement.allowance))
                    - Decimal(str(entitlement.consumed)),
                )

                next_reset_at = (
                    entitlement.next_reset_at.isoformat()
                    if entitlement.next_reset_at
                    else None
                )

                reset_interval_hours = (
                    entitlement.reset_interval_hours
                )

        else:

            capacity = self._tier_capacity_repository.get(user_id)

            if capacity is not None:

                if now < capacity.period_ends_at:

                    included_balance = max(
                        Decimal("0"),
                        capacity.allowance - capacity.consumed,
                    )

                next_reset_at = (
                    capacity.period_ends_at.isoformat()
                    if capacity.period_ends_at
                    else None
                )

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
            "next_reset_at": next_reset_at,
            "reset_interval_hours": reset_interval_hours,
        }