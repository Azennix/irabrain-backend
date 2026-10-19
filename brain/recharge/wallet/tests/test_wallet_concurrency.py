from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from decimal import Decimal
from threading import Barrier

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from database.database import SessionLocal
from brain.recharge.wallet.repository import BrainWalletRepository
from brain.recharge.wallet.service import BrainWalletService
from brain.recharge.wallet.transaction_repository import (
    BrainTransactionRepository,
)
from brain.recharge.wallet.wallet_operations import BrainWalletOperations
from brain.recharge.wallet.brain_transaction_model import (
    BrainTransactionModel,
)


def make_operations(session):
    return BrainWalletOperations(
        wallet_repository=BrainWalletRepository(session),
        transaction_repository=BrainTransactionRepository(session),
        wallet_service=BrainWalletService(),
    )


def test_concurrent_duplicate_recharge_credits_once():
    user_id = 999981
    reference_id = "concurrency-payment-test-001"

    # Create a fresh wallet and commit setup before concurrent requests.
    with SessionLocal() as session:
        operations = make_operations(session)
        operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id="concurrency-initial-001",
        )
        session.commit()

    barrier = Barrier(2)

    def recharge():
        with SessionLocal() as session:
            operations = make_operations(session)
            barrier.wait()

            try:
                operations.recharge(
                    user_id=user_id,
                    units=Decimal("100"),
                    reference_id=reference_id,
                )
                session.commit()
                return "credited"
            except IntegrityError:
                session.rollback()
                return "conflict"

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: recharge(), range(2)))

        with SessionLocal() as session:
            wallet = BrainWalletRepository(session).get(user_id)

            assert wallet is not None
            assert wallet.current_balance == Decimal("200")

            count = (
                session.query(func.count(BrainTransactionModel.id))
                .filter(
                    BrainTransactionModel.reference_id == reference_id
                )
                .scalar()
            )

            assert count == 1

    finally:
        with SessionLocal() as session:
            session.query(BrainTransactionModel).filter(
                BrainTransactionModel.user_id == user_id
            ).delete(synchronize_session=False)

            from brain.recharge.wallet.brain_wallet_model import (
                BrainWalletModel,
            )

            session.query(BrainWalletModel).filter(
                BrainWalletModel.user_id == user_id
            ).delete(synchronize_session=False)

            session.commit()


def test_concurrent_consumption_cannot_overspend():
    user_id = 999980

    # Prepare a wallet with 100 units.
    with SessionLocal() as session:
        operations = make_operations(session)

        operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id="concurrency-consumption-initial-001",
        )
        session.commit()

    barrier = Barrier(2)

    def consume(reference_id):
        with SessionLocal() as session:
            operations = make_operations(session)
            barrier.wait()

            try:
                operations.consume(
                    user_id=user_id,
                    units=Decimal("70"),
                    reference_id=reference_id,
                )
                session.commit()
                return "success"

            except Exception as exc:
                session.rollback()

                if isinstance(exc, ValueError):
                    return "insufficient"

                raise

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(
                    consume,
                    [
                        "concurrency-consume-001",
                        "concurrency-consume-002",
                    ],
                )
            )

        assert results.count("success") == 1
        assert results.count("insufficient") == 1

        with SessionLocal() as session:
            wallet = BrainWalletRepository(session).get(user_id)

            assert wallet is not None
            assert wallet.current_balance == Decimal("30")
            assert wallet.lifetime_consumed == Decimal("70")

    finally:
        with SessionLocal() as session:
            from brain.recharge.wallet.brain_wallet_model import (
                BrainWalletModel,
            )

            session.query(BrainTransactionModel).filter(
                BrainTransactionModel.user_id == user_id
            ).delete(synchronize_session=False)

            session.query(BrainWalletModel).filter(
                BrainWalletModel.user_id == user_id
            ).delete(synchronize_session=False)

            session.commit()


def test_recharge_rolls_back_when_transaction_record_fails():
    user_id = 999979
    reference_id = "rollback-recharge-test-001"

    try:
        # Prepare and commit a real wallet with 100 units.
        with SessionLocal() as session:
            operations = make_operations(session)

            operations.recharge(
                user_id=user_id,
                units=Decimal("100"),
                reference_id="rollback-initial-recharge-001",
            )
            session.commit()

        # Simulate transaction-record creation failing.
        with SessionLocal() as session:
            operations = make_operations(session)

            with patch.object(
                operations._transaction_repository,
                "create",
                side_effect=RuntimeError("Simulated transaction failure"),
            ):
                try:
                    operations.recharge(
                        user_id=user_id,
                        units=Decimal("50"),
                        reference_id=reference_id,
                    )
                    assert False, "Expected simulated failure"
                except RuntimeError as exc:
                    assert "Simulated transaction failure" in str(exc)
                    session.rollback()

        # Verify that the failed recharge didn't change the balance.
        with SessionLocal() as session:
            wallet = BrainWalletRepository(session).get(user_id)

            assert wallet is not None
            assert wallet.current_balance == Decimal("100")
            assert wallet.lifetime_purchased == Decimal("100")

            transaction = BrainTransactionRepository(
                session
            ).get_by_reference_id(reference_id)

            assert transaction is None

    finally:
        # Clean up only this dedicated test user's data.
        with SessionLocal() as session:
            session.query(BrainTransactionModel).filter(
                BrainTransactionModel.user_id == user_id
            ).delete(synchronize_session=False)

            from brain.recharge.wallet.brain_wallet_model import (
                BrainWalletModel,
            )

            session.query(BrainWalletModel).filter(
                BrainWalletModel.user_id == user_id
            ).delete(synchronize_session=False)

            session.commit()