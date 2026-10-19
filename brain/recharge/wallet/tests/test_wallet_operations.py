from decimal import Decimal

from brain.recharge.wallet.repository import BrainWalletRepository
from brain.recharge.wallet.service import BrainWalletService
from brain.recharge.wallet.transaction_repository import (
    BrainTransactionRepository,
)
from brain.recharge.wallet.wallet_operations import BrainWalletOperations
from database.database import SessionLocal


def test_atomic_recharge():
    session = SessionLocal()

    try:
        wallet_repository = BrainWalletRepository(session)
        transaction_repository = BrainTransactionRepository(session)
        wallet_service = BrainWalletService()

        operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=wallet_service,
        )

        user_id = 999997

        wallet = operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id="test-recharge-001",
            metadata={
                "source": "wallet_operation_test",
            },
        )

        assert wallet.user_id == user_id
        assert wallet.current_balance == Decimal("100")
        assert wallet.lifetime_purchased == Decimal("100")
        assert wallet.lifetime_consumed == Decimal("0")

        session.rollback()

    finally:
        session.close()


def test_atomic_consumption():
    session = SessionLocal()

    try:
        wallet_repository = BrainWalletRepository(session)
        transaction_repository = BrainTransactionRepository(session)
        wallet_service = BrainWalletService()

        operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=wallet_service,
        )

        user_id = 999996

        operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id="test-initial-recharge",
        )

        wallet = operations.consume(
            user_id=user_id,
            units=Decimal("25"),
            reference_id="test-consumption-001",
            metadata={
                "capability": "chat",
            },
        )

        assert wallet.current_balance == Decimal("75")
        assert wallet.lifetime_purchased == Decimal("100")
        assert wallet.lifetime_consumed == Decimal("25")

        session.rollback()

    finally:
        session.close()


def test_insufficient_balance_does_not_consume():
    session = SessionLocal()

    try:
        wallet_repository = BrainWalletRepository(session)
        transaction_repository = BrainTransactionRepository(session)
        wallet_service = BrainWalletService()

        operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=wallet_service,
        )

        user_id = 999995

        operations.recharge(
            user_id=user_id,
            units=Decimal("10"),
            reference_id="test-small-recharge",
        )

        try:
            operations.consume(
                user_id=user_id,
                units=Decimal("25"),
                reference_id="test-failed-consumption",
            )
            assert False, "Expected insufficient balance error"
        except ValueError as exc:
            assert "Insufficient Brain Balance" in str(exc)

        wallet = wallet_repository.get(user_id)

        assert wallet is not None
        assert wallet.current_balance == Decimal("10")
        assert wallet.lifetime_consumed == Decimal("0")

        session.rollback()

    finally:
        session.close()


def test_duplicate_recharge_does_not_double_credit():
    session = SessionLocal()

    try:
        wallet_repository = BrainWalletRepository(session)
        transaction_repository = BrainTransactionRepository(session)
        wallet_service = BrainWalletService()

        operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=wallet_service,
        )

        user_id = 999993
        reference_id = "payment-idempotency-test-001"

        first_wallet = operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id=reference_id,
        )

        second_wallet = operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id=reference_id,
        )

        assert first_wallet.current_balance == Decimal("100")
        assert second_wallet.current_balance == Decimal("100")

        loaded = wallet_repository.get(user_id)

        assert loaded is not None
        assert loaded.current_balance == Decimal("100")
        assert loaded.lifetime_purchased == Decimal("100")

        session.rollback()

    finally:
        session.close()

def test_recharge_reference_cannot_be_used_by_another_user():
    session = SessionLocal()

    try:
        wallet_repository = BrainWalletRepository(session)
        transaction_repository = BrainTransactionRepository(session)
        wallet_service = BrainWalletService()

        operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=wallet_service,
        )

        original_user_id = 999992
        another_user_id = 999991
        reference_id = "payment-owner-test-001"

        operations.recharge(
            user_id=original_user_id,
            units=Decimal("100"),
            reference_id=reference_id,
        )

        try:
            operations.recharge(
                user_id=another_user_id,
                units=Decimal("100"),
                reference_id=reference_id,
            )
            assert False, "Expected reference ownership error"
        except ValueError as exc:
            assert "different user" in str(exc)

        original_wallet = wallet_repository.get(
            original_user_id
        )

        assert original_wallet is not None
        assert original_wallet.current_balance == Decimal("100")

        another_wallet = wallet_repository.get(
            another_user_id
        )

        assert another_wallet is None

        session.rollback()

    finally:
        session.close()


def test_distinct_recharge_references_credit_separately():
    session = SessionLocal()

    try:
        wallet_repository = BrainWalletRepository(session)
        transaction_repository = BrainTransactionRepository(session)

        operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=BrainWalletService(),
        )

        user_id = 999990

        first_wallet = operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id="payment-distinct-001",
        )

        second_wallet = operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id="payment-distinct-002",
        )

        assert first_wallet.current_balance == Decimal("100")
        assert second_wallet.current_balance == Decimal("200")
        assert second_wallet.lifetime_purchased == Decimal("200")

        session.rollback()

    finally:
        session.close()