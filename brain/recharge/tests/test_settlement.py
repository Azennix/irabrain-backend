from datetime import datetime, timezone
from decimal import Decimal

from brain.recharge.calculator import (
    BrainUnitCalculator,
    CostBasedBrainUnitPolicy,
)
from brain.recharge.cost.cost_resolver import ExecutionCostResolver
from brain.recharge.cost.passthrough_cost_source import (
    PassthroughExecutionCostSource,
)
from brain.recharge.entitlement.consumption import (
    FreeBrainConsumptionPolicy,
)
from brain.recharge.entitlement.repository import (
    FreeBrainEntitlementRepository,
)
from brain.recharge.entitlement.reset_policy import (
    FreeBrainResetPolicy,
)
from brain.recharge.entitlement.service import (
    FreeBrainEntitlementService,
)
from brain.recharge.included_capacity_service import (
    IncludedBrainCapacityService,
)
from brain.recharge.models import BrainUsageContext
from brain.recharge.settlement import BrainUsageSettlementService
from brain.recharge.settlement_repository import (
    BrainSettlementRepository,
)
from brain.recharge.wallet.repository import BrainWalletRepository
from brain.recharge.wallet.service import BrainWalletService
from brain.recharge.wallet.transaction_repository import (
    BrainTransactionRepository,
)
from brain.recharge.wallet.wallet_operations import BrainWalletOperations
from brain.tier.capacity.capacity_service import (
    PersistentTierCapacityService,
)
from brain.tier.capacity.repository import (
    TierBrainCapacityRepository,
)
from brain.tier.models import BrainTier
from brain.tier.capacity.models import TierBrainCapacity
from database.database import SessionLocal
import pytest
from sqlalchemy import text





def build_free_brain_service(session):
    free_brain_repository = FreeBrainEntitlementRepository(session)

    return FreeBrainEntitlementService(
        repository=free_brain_repository,
        reset_policy=FreeBrainResetPolicy(),
        consumption_policy=FreeBrainConsumptionPolicy(),
    )

from sqlalchemy import text


def clear_test_tier_capacity(session, user_id: int) -> None:
    """Remove stale capacity rows for synthetic test users."""
    allowed_test_users = {999984, 999983, 999982, 999981}

    if user_id not in allowed_test_users:
        raise ValueError(
            f"Unexpected test user ID for capacity cleanup: {user_id}"
        )

    session.execute(
        text(
            """
            DELETE FROM tier_brain_capacities
            WHERE user_id = :user_id
            """
        ),
        {"user_id": user_id},
    )
    session.flush()


def build_settlement_service(session, free_brain_service):
    wallet_repository = BrainWalletRepository(session)
    transaction_repository = BrainTransactionRepository(session)
    settlement_repository = BrainSettlementRepository(session)
    wallet_service = BrainWalletService()

    wallet_operations = BrainWalletOperations(
        wallet_repository=wallet_repository,
        transaction_repository=transaction_repository,
        wallet_service=wallet_service,
    )

    cost_resolver = ExecutionCostResolver(
        sources=[
            PassthroughExecutionCostSource(),
        ]
    )

    tier_capacity_repository = TierBrainCapacityRepository(session)
    clear_test_tier_capacity(session, 999984)
    tier_capacity_service = PersistentTierCapacityService(
        repository=tier_capacity_repository,
    )

    included_capacity_service = IncludedBrainCapacityService(
        free_brain_service=free_brain_service,
        tier_capacity_service=tier_capacity_service,
    )

    settlement_service = BrainUsageSettlementService(
        cost_resolver=cost_resolver,
        wallet_operations=wallet_operations,
        included_capacity_service=included_capacity_service,
        settlement_repository=settlement_repository,
    )

    unit_calculator = BrainUnitCalculator(
        policy=CostBasedBrainUnitPolicy(
            unit_cost=Decimal("0.01"),
            version="v1",
        )
    )

    return (
        settlement_service,
        unit_calculator,
        wallet_repository,
        transaction_repository,
    )


def test_settlement_consumes_free_brain_before_paid_brain():
    session = SessionLocal()

    try:
        user_id = 999990

        free_brain_service = build_free_brain_service(session)

        free_brain_service.get_or_create(
            user_id=user_id,
            allowance=Decimal("3"),
            reset_interval_hours=24,
            now=datetime(
                2026,
                10,
                4,
                10,
                0,
                0,
                tzinfo=timezone.utc,
            ),
        )

        (
            settlement_service,
            unit_calculator,
            wallet_repository,
            transaction_repository,
        ) = build_settlement_service(
            session=session,
            free_brain_service=free_brain_service,
        )

        wallet_operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=BrainWalletService(),
        )

        wallet_operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id="settlement-initial-recharge-001",
            metadata={
                "source": "settlement_test",
            },
        )

        context = BrainUsageContext(
            request_id="settlement-test-001",
            user_id=user_id,
            brain_tier=BrainTier.FREE,
            capability="chat",
            task_type="conversation",
            provider="ollama",
            model="qwen2.5:7b",
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
            estimated_cost=0.05,
            metadata={
                "cost_currency": "USD",
            },
        )

        result = settlement_service.settle(
            context=context,
            unit_calculator=unit_calculator,
        )

        # $0.05 / $0.01 = 5 Brain Units
        assert result.units == Decimal("5.00")
        assert result.calculation_version == "v1"
        assert result.basis == "execution_cost"

        # Free Brain should consume 3 units first.
        free_brain_repository = FreeBrainEntitlementRepository(session)

        free_entitlement = free_brain_repository.get(user_id)

        assert free_entitlement is not None
        assert free_entitlement.consumed == Decimal("3")

        # Remaining 2 units should come from paid Brain.
        wallet = wallet_repository.get(user_id)

        assert wallet is not None
        assert wallet.current_balance == Decimal("98")
        assert wallet.lifetime_purchased == Decimal("100")
        assert wallet.lifetime_consumed == Decimal("2")

        # Paid transaction should contain only the paid portion.
        transaction = transaction_repository.get_by_reference_id(
            "settlement-test-001"
        )

        assert transaction is not None
        assert transaction.user_id == user_id
        assert transaction.units == Decimal("2")
        assert transaction.reference_id == "settlement-test-001"

        session.rollback()

    finally:
        session.close()


def test_duplicate_settlement_does_not_consume_twice():
    session = SessionLocal()

    try:
        user_id = 999989

        free_brain_service = build_free_brain_service(session)

        free_brain_service.get_or_create(
            user_id=user_id,
            allowance=Decimal("100"),
            reset_interval_hours=24,
            now=datetime(
                2026,
                10,
                4,
                10,
                0,
                0,
                tzinfo=timezone.utc,
            ),
        )

        (
            settlement_service,
            unit_calculator,
            wallet_repository,
            transaction_repository,
        ) = build_settlement_service(
            session=session,
            free_brain_service=free_brain_service,
        )

        wallet_operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=BrainWalletService(),
        )

        wallet_operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id="duplicate-settlement-recharge-001",
        )

        context = BrainUsageContext(
            request_id="duplicate-settlement-001",
            user_id=user_id,
            brain_tier=BrainTier.FREE,
            capability="chat",
            task_type="conversation",
            provider="ollama",
            model="qwen2.5:7b",
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
            estimated_cost=0.05,
            metadata={
                "cost_currency": "USD",
            },
        )

        first_result = settlement_service.settle(
            context=context,
            unit_calculator=unit_calculator,
        )

        second_result = settlement_service.settle(
            context=context,
            unit_calculator=unit_calculator,
        )

        transaction = transaction_repository.get_by_reference_id(
            "duplicate-settlement-001"
        )

        assert transaction is None

        assert first_result.units == Decimal("5.00")
        assert second_result.units == Decimal("5")
        assert second_result.basis == "idempotent_replay"

        free_brain_repository = FreeBrainEntitlementRepository(session)

        free_entitlement = free_brain_repository.get(user_id)

        assert free_entitlement is not None
        assert free_entitlement.consumed == Decimal("5")

        wallet = wallet_repository.get(user_id)

        assert wallet is not None
        assert wallet.current_balance == Decimal("100")
        assert wallet.lifetime_purchased == Decimal("100")
        assert wallet.lifetime_consumed == Decimal("0")

        session.rollback()

    finally:
        session.close()


def test_settlement_fails_without_sufficient_brain_balance():
    session = SessionLocal()

    try:
        user_id = 999988

        free_brain_service = build_free_brain_service(session)

        free_brain_service.get_or_create(
            user_id=user_id,
            allowance=Decimal("0.01"),
            reset_interval_hours=24,
            now=datetime(
                2026,
                10,
                4,
                10,
                0,
                0,
                tzinfo=timezone.utc,
            ),
        )

        (
            settlement_service,
            unit_calculator,
            wallet_repository,
            transaction_repository,
        ) = build_settlement_service(
            session=session,
            free_brain_service=free_brain_service,
        )

        wallet_operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=BrainWalletService(),
        )

        wallet_operations.recharge(
            user_id=user_id,
            units=Decimal("2"),
            reference_id="insufficient-settlement-recharge-001",
        )

        context = BrainUsageContext(
            request_id="insufficient-settlement-001",
            user_id=user_id,
            brain_tier=BrainTier.FREE,
            capability="chat",
            task_type="conversation",
            provider="ollama",
            model="qwen2.5:7b",
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
            estimated_cost=0.05,
            metadata={
                "cost_currency": "USD",
            },
        )

        try:
            settlement_service.settle(
                context=context,
                unit_calculator=unit_calculator,
            )
            assert False, "Expected insufficient Brain Balance error"
        except ValueError as exc:
            assert "Insufficient Brain Balance" in str(exc)

        free_brain_repository = FreeBrainEntitlementRepository(session)

        free_entitlement = free_brain_repository.get(user_id)

        assert free_entitlement is not None
        assert free_entitlement.consumed == Decimal("0.01")

        wallet = wallet_repository.get(user_id)

        assert wallet is not None
        assert wallet.current_balance == Decimal("2")
        assert wallet.lifetime_purchased == Decimal("2")
        assert wallet.lifetime_consumed == Decimal("0")

        transaction = transaction_repository.get_by_reference_id(
            "insufficient-settlement-001"
        )

        assert transaction is None

        session.rollback()

    finally:
        session.close()

def test_thalamus_settlement_consumes_included_capacity_before_paid_brain():
    session = SessionLocal()

    try:
        user_id = 999987

        free_brain_service = build_free_brain_service(session)

        tier_capacity_repository = TierBrainCapacityRepository(session)

        capacity = TierBrainCapacity(
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            allowance=Decimal("3000"),
            consumed=Decimal("0"),
            period_started_at=datetime(
                2026,
                10,
                8,
                10,
                0,
                0,
                tzinfo=timezone.utc,
            ),
            period_ends_at=datetime(
                2026,
                11,
                8,
                10,
                0,
                0,
                tzinfo=timezone.utc,
            ),
        )

        tier_capacity_repository.create(capacity)

        (
            settlement_service,
            unit_calculator,
            wallet_repository,
            transaction_repository,
        ) = build_settlement_service(
            session=session,
            free_brain_service=free_brain_service,
        )

        wallet_operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=BrainWalletService(),
        )

        wallet_operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id="thalamus-initial-recharge-001",
        )

        context = BrainUsageContext(
            request_id="thalamus-settlement-001",
            user_id=user_id,
            brain_tier=BrainTier.THALAMUS,
            capability="chat",
            task_type="conversation",
            provider="ollama",
            model="qwen2.5:7b",
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
            estimated_cost=0.05,
            metadata={
                "cost_currency": "USD",
            },
        )

        result = settlement_service.settle(
            context=context,
            unit_calculator=unit_calculator,
        )

        assert result.units == Decimal("5.00")

        updated_capacity = tier_capacity_repository.get(user_id)

        assert updated_capacity is not None
        assert updated_capacity.allowance == Decimal("3000")
        assert updated_capacity.consumed == Decimal("5")
        assert updated_capacity.remaining == Decimal("2995")

        wallet = wallet_repository.get(user_id)

        assert wallet is not None
        assert wallet.current_balance == Decimal("100")
        assert wallet.lifetime_purchased == Decimal("100")
        assert wallet.lifetime_consumed == Decimal("0")

        transaction = transaction_repository.get_by_reference_id(
            "thalamus-settlement-001"
        )

        assert transaction is None

        session.rollback()

    finally:
        session.close()

def test_thalamus_settlement_uses_paid_brain_after_included_capacity():
    session = SessionLocal()

    try:
        user_id = 999986

        free_brain_service = build_free_brain_service(session)

        tier_capacity_repository = TierBrainCapacityRepository(session)

        capacity = TierBrainCapacity(
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            allowance=Decimal("3000"),
            consumed=Decimal("2998"),
            period_started_at=datetime(
                2026,
                10,
                8,
                10,
                0,
                0,
                tzinfo=timezone.utc,
            ),
            period_ends_at=datetime(
                2026,
                11,
                8,
                10,
                0,
                0,
                tzinfo=timezone.utc,
            ),
        )

        tier_capacity_repository.create(capacity)

        (
            settlement_service,
            unit_calculator,
            wallet_repository,
            transaction_repository,
        ) = build_settlement_service(
            session=session,
            free_brain_service=free_brain_service,
        )

        wallet_operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=BrainWalletService(),
        )

        wallet_operations.recharge(
            user_id=user_id,
            units=Decimal("3000"),
            reference_id="thalamus-fallback-recharge-001",
        )

        context = BrainUsageContext(
            request_id="thalamus-fallback-settlement-001",
            user_id=user_id,
            brain_tier=BrainTier.THALAMUS,
            capability="chat",
            task_type="conversation",
            provider="ollama",
            model="qwen2.5:7b",
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
            estimated_cost=30,
            metadata={
                "cost_currency": "USD",
            },
        )

        result = settlement_service.settle(
            context=context,
            unit_calculator=unit_calculator,
        )

        # $30 / $0.01 = 3000 Brain Units
        assert result.units == Decimal("3000.00")

        updated_capacity = tier_capacity_repository.get(user_id)

        assert updated_capacity is not None
        assert updated_capacity.allowance == Decimal("3000")
        assert updated_capacity.consumed == Decimal("3000")
        assert updated_capacity.remaining == Decimal("0")

        # 2998 included + 2 paid
        wallet = wallet_repository.get(user_id)

        assert wallet is not None
        assert wallet.current_balance == Decimal("2")
        assert wallet.lifetime_purchased == Decimal("3000")
        assert wallet.lifetime_consumed == Decimal("2998")

        transaction = transaction_repository.get_by_reference_id(
            "thalamus-fallback-settlement-001"
        )

        assert transaction is not None
        assert transaction.user_id == user_id
        assert transaction.units == Decimal("2998")
        assert transaction.reference_id == (
            "thalamus-fallback-settlement-001"
        )

        session.rollback()

    finally:
        session.close()

def test_thalamus_settlement_rolls_back_included_capacity_when_paid_balance_is_insufficient():
    user_id = 999984

    session = SessionLocal()

    try:
        free_brain_service = build_free_brain_service(session)
        settlement_service, unit_calculator, wallet_repository, _ = (
            build_settlement_service(session, free_brain_service)
        )

        tier_capacity_repository = TierBrainCapacityRepository(session)

        now = datetime.now(timezone.utc)

        tier_capacity_repository.create(
            TierBrainCapacity(
                user_id=user_id,
                tier=BrainTier.THALAMUS,
                allowance=Decimal("3000"),
                consumed=Decimal("2998"),
                period_started_at=now,
                period_ends_at=now.replace(
                    year=now.year + 1,
                ),
            )
        )

        wallet_operations = settlement_service._wallet_operations

        wallet_operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id="thalamus-atomicity-recharge-001",
        )
        session.commit()

        context = BrainUsageContext(
            request_id="thalamus-atomicity-001",
            user_id=user_id,
            brain_tier=BrainTier.THALAMUS,
            provider="test",
            model="test-model",
            estimated_cost=30.0,
        )

        try:
            settlement_service.settle(
                context=context,
                unit_calculator=unit_calculator,
            )
            assert False, "Expected insufficient Brain Balance."
        except ValueError as exc:
            assert str(exc) == "Insufficient Brain Balance."

        session.rollback()

        capacity = tier_capacity_repository.get(user_id)
        wallet = wallet_repository.get(user_id)

        assert capacity.consumed == Decimal("2998")
        assert capacity.remaining == Decimal("2")

        assert wallet.current_balance == Decimal("100")
        assert wallet.lifetime_purchased == Decimal("100")
        assert wallet.lifetime_consumed == Decimal("0")

    finally:
        session.rollback()
        session.close()



def test_hippocampus_settlement_consumes_included_capacity():
    user_id = 999983

    session = SessionLocal()

    try:
        free_brain_service = build_free_brain_service(session)
        settlement_service, unit_calculator, wallet_repository, _ = (
            build_settlement_service(session, free_brain_service)
        )

        tier_capacity_repository = TierBrainCapacityRepository(session)

        now = datetime.now(timezone.utc)

        tier_capacity_repository.create(
            TierBrainCapacity(
                user_id=user_id,
                tier=BrainTier.HIPPOCAMPUS,
                allowance=Decimal("10000"),
                consumed=Decimal("0"),
                period_started_at=now,
                period_ends_at=now.replace(
                    year=now.year + 1,
                ),
            )
        )

        wallet_operations = settlement_service._wallet_operations

        wallet_operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id="hippocampus-settlement-recharge-001",
        )

        session.commit()

        context = BrainUsageContext(
            request_id="hippocampus-settlement-001",
            user_id=user_id,
            brain_tier=BrainTier.HIPPOCAMPUS,
            provider="test",
            model="test-model",
            estimated_cost=1.0,
        )

        result = settlement_service.settle(
            context=context,
            unit_calculator=unit_calculator,
        )

        assert result.units == Decimal("100")

        capacity = tier_capacity_repository.get(user_id)

        assert capacity.allowance == Decimal("10000")
        assert capacity.consumed == Decimal("100")
        assert capacity.remaining == Decimal("9900")

        wallet = wallet_repository.get(user_id)

        assert wallet.current_balance == Decimal("100")
        assert wallet.lifetime_purchased == Decimal("100")
        assert wallet.lifetime_consumed == Decimal("0")

        session.commit()

    finally:
        session.rollback()
        session.close()

def test_hippocampus_settlement_uses_paid_brain_after_included_capacity():
    user_id = 999982

    session = SessionLocal()

    try:
        free_brain_service = build_free_brain_service(session)
        settlement_service, unit_calculator, wallet_repository, transaction_repository = (
            build_settlement_service(session, free_brain_service)
        )

        tier_capacity_repository = TierBrainCapacityRepository(session)

        now = datetime.now(timezone.utc)

        tier_capacity_repository.create(
            TierBrainCapacity(
                user_id=user_id,
                tier=BrainTier.HIPPOCAMPUS,
                allowance=Decimal("10000"),
                consumed=Decimal("9998"),
                period_started_at=now,
                period_ends_at=now.replace(year=now.year + 1),
            )
        )

        wallet_operations = settlement_service._wallet_operations

        wallet_operations.recharge(
            user_id=user_id,
            units=Decimal("3000"),
            reference_id="hippocampus-fallback-recharge-001",
        )

        session.commit()

        context = BrainUsageContext(
            request_id="hippocampus-fallback-001",
            user_id=user_id,
            brain_tier=BrainTier.HIPPOCAMPUS,
            provider="test",
            model="test-model",
            estimated_cost=30.0,
        )

        result = settlement_service.settle(
            context=context,
            unit_calculator=unit_calculator,
        )

        assert result.units == Decimal("3000")

        capacity = tier_capacity_repository.get(user_id)

        assert capacity.allowance == Decimal("10000")
        assert capacity.consumed == Decimal("10000")
        assert capacity.remaining == Decimal("0")

        wallet = wallet_repository.get(user_id)

        assert wallet.current_balance == Decimal("2")
        assert wallet.lifetime_purchased == Decimal("3000")
        assert wallet.lifetime_consumed == Decimal("2998")

        transaction = transaction_repository.get_by_reference_id(
            "hippocampus-fallback-001"
        )

        assert transaction is not None
        assert transaction.units == Decimal("2998")

        session.commit()

    finally:
        session.rollback()
        session.close()


def test_thalamus_settlement_rejects_expired_included_capacity():
    user_id = 999981

    session = SessionLocal()

    try:
        free_brain_service = build_free_brain_service(session)
        settlement_service, unit_calculator, wallet_repository, _ = (
            build_settlement_service(session, free_brain_service)
        )

        tier_capacity_repository = TierBrainCapacityRepository(session)

        now = datetime.now(timezone.utc)

        tier_capacity_repository.create(
            TierBrainCapacity(
                user_id=user_id,
                tier=BrainTier.THALAMUS,
                allowance=Decimal("3000"),
                consumed=Decimal("0"),
                period_started_at=now.replace(year=now.year - 1),
                period_ends_at=now.replace(year=now.year - 1, month=12, day=31),
            )
        )

        session.commit()

        context = BrainUsageContext(
            request_id="thalamus-expired-001",
            user_id=user_id,
            brain_tier=BrainTier.THALAMUS,
            provider="test",
            model="test-model",
            estimated_cost=0.05,
        )

        with pytest.raises(ValueError, match="period has expired"):
            settlement_service.settle(
                context=context,
                unit_calculator=unit_calculator,
            )

        session.rollback()

        capacity = tier_capacity_repository.get(user_id)

        assert capacity.consumed == Decimal("0")
        assert capacity.remaining == Decimal("3000")

        wallet = wallet_repository.get(user_id)

        assert wallet is None

    finally:
        session.rollback()
        session.close()