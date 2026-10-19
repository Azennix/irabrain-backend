from datetime import datetime
from decimal import Decimal

from brain.recharge.wallet.models import BrainWallet
from brain.recharge.wallet.repository import BrainWalletRepository
from database.database import SessionLocal


def test_update_brain_wallet():
    session = SessionLocal()

    try:
        repository = BrainWalletRepository(session)

        user_id = 999998

        wallet = repository.create(user_id)

        updated_wallet = BrainWallet(
            user_id=user_id,
            current_balance=Decimal("150"),
            lifetime_purchased=Decimal("150"),
            lifetime_consumed=Decimal("0"),
            updated_at=datetime.utcnow(),
        )

        saved = repository.update(updated_wallet)

        assert saved.user_id == user_id
        assert saved.current_balance == Decimal("150")
        assert saved.lifetime_purchased == Decimal("150")
        assert saved.lifetime_consumed == Decimal("0")

        loaded = repository.get(user_id)

        assert loaded is not None
        assert loaded.current_balance == Decimal("150")
        assert loaded.lifetime_purchased == Decimal("150")
        assert loaded.lifetime_consumed == Decimal("0")

        session.rollback()

    finally:
        session.close()