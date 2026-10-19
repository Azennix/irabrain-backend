from decimal import Decimal

from brain.recharge.balance_service import BrainBalanceService
from brain.recharge.entitlement.models import FreeBrainEntitlement
from brain.recharge.entitlement.repository import (
    FreeBrainEntitlementRepository,
)
from brain.recharge.entitlement.reset_policy import (
    FreeBrainResetPolicy,
)
from brain.recharge.entitlement.consumption import (
    FreeBrainConsumptionPolicy,
)
from brain.recharge.entitlement.service import (
    FreeBrainEntitlementService,
)
from brain.recharge.wallet.repository import BrainWalletRepository
from brain.recharge.wallet.service import BrainWalletService
from brain.recharge.wallet.transaction_repository import (
    BrainTransactionRepository,
)
from brain.recharge.wallet.wallet_operations import (
    BrainWalletOperations,
)
from database.database import SessionLocal
from brain.tier.capacity.repository import TierBrainCapacityRepository


def build_free_brain_service(session):
    repository = FreeBrainEntitlementRepository(session)

    return FreeBrainEntitlementService(
        repository=repository,
        reset_policy=FreeBrainResetPolicy(),
        consumption_policy=FreeBrainConsumptionPolicy(),
    )


def test_balance_combines_free_and_paid_brain():
    session = SessionLocal()

    try:
        user_id = 999987

        free_brain_service = build_free_brain_service(session)

        free_brain_service.get_or_create(
            user_id=user_id,
            allowance=Decimal("100"),
            reset_interval_hours=24,
            now=datetime_now(),
        )

        free_brain_service.consume(
            user_id=user_id,
            requested_units=25,
            now=datetime_now(),
        )

        wallet_repository = BrainWalletRepository(session)
        transaction_repository = BrainTransactionRepository(session)

        wallet_operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=BrainWalletService(),
        )

        wallet_operations.recharge(
            user_id=user_id,
            units=Decimal("500"),
            reference_id="balance-test-recharge-001",
        )

        balance_service = BrainBalanceService(
            wallet_repository=wallet_repository,
            free_brain_service=free_brain_service,
            tier_capacity_repository=TierBrainCapacityRepository(session),

        )

        balance = balance_service.get_balance(user_id)

        assert balance["included_balance"] == Decimal("75")
        assert balance["paid_balance"] == Decimal("500")
        assert balance["total_balance"] == Decimal("575")

    finally:
        session.rollback()
        session.close()


def test_balance_returns_zero_for_user_without_brain():
    session = SessionLocal()

    try:
        user_id = 999986

        balance_service = BrainBalanceService(
            wallet_repository=BrainWalletRepository(session),
            free_brain_service=build_free_brain_service(session),
            tier_capacity_repository=TierBrainCapacityRepository(session),

        )

        balance = balance_service.get_balance(user_id)

        assert balance["included_balance"] == Decimal("0")
        assert balance["paid_balance"] == Decimal("0")
        assert balance["total_balance"] == Decimal("0")

    finally:
        session.rollback()
        session.close()


def test_balance_rejects_invalid_user_id():
    session = SessionLocal()

    try:
        balance_service = BrainBalanceService(
            wallet_repository=BrainWalletRepository(session),
            free_brain_service=build_free_brain_service(session),
            tier_capacity_repository=TierBrainCapacityRepository(session),


        )

        try:
            balance_service.get_balance(0)
            assert False, "Expected invalid user ID error"
        except ValueError as exc:
            assert "User ID must be greater than zero" in str(exc)

    finally:
        session.rollback()
        session.close()


def datetime_now():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc)



def test_balance_uses_thalamus_included_capacity_and_paid_balance():
    session = SessionLocal()

    try:
        from brain.tier.models import BrainTier
        from brain.tier.capacity.capacity_model import TierBrainCapacityModel
        from datetime import datetime, timezone, timedelta

        user_id = 999988
        now = datetime.now(timezone.utc)

        capacity = TierBrainCapacityModel(
            user_id=user_id,
            tier=BrainTier.THALAMUS.value,
            allowance=Decimal("3000"),
            consumed=Decimal("250"),
            period_started_at=now,
            period_ends_at=now + timedelta(days=30),
        )

        session.add(capacity)
        session.flush()

        wallet_repository = BrainWalletRepository(session)
        transaction_repository = BrainTransactionRepository(session)

        wallet_operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=BrainWalletService(),
        )

        wallet_operations.recharge(
            user_id=user_id,
            units=Decimal("500"),
            reference_id="balance-test-thalamus-001",
        )

        # This test will initially fail until BrainBalanceService
        # becomes tier-aware.
        balance_service = BrainBalanceService(
            wallet_repository=wallet_repository,
            free_brain_service=build_free_brain_service(session),
            tier_capacity_repository=TierBrainCapacityRepository(session),
        )

        balance = balance_service.get_balance(user_id)

        assert balance["included_balance"] == Decimal("2750")
        assert balance["paid_balance"] == Decimal("500")
        assert balance["total_balance"] == Decimal("3250")

    finally:
        session.rollback()
        session.close()