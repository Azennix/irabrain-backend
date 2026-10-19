from decimal import Decimal

from sqlalchemy.orm import Session

from brain.recharge.wallet.brain_wallet_model import BrainWalletModel
from brain.recharge.wallet.models import BrainWallet


class BrainWalletRepository:
    def __init__(self, session: Session):
        if session is None:
            raise ValueError("Database session is required.")

        self._session = session

    def get(self, user_id: int) -> BrainWallet | None:
        model = (
            self._session.query(BrainWalletModel)
            .filter(BrainWalletModel.user_id == user_id)
             .with_for_update()
            .first()
        )

        if model is None:
            return None

        return BrainWallet(
            user_id=model.user_id,
            current_balance=Decimal(model.current_balance),
            lifetime_purchased=Decimal(model.lifetime_purchased),
            lifetime_consumed=Decimal(model.lifetime_consumed),
            updated_at=model.updated_at,
        )

    def create(self, user_id: int) -> BrainWallet:
        existing = self.get(user_id)

        if existing is not None:
            raise ValueError("Brain wallet already exists.")

        model = BrainWalletModel(
            user_id=user_id,
            current_balance=Decimal("0"),
            lifetime_purchased=Decimal("0"),
            lifetime_consumed=Decimal("0"),
        )

        self._session.add(model)
        self._session.flush()

        return BrainWallet(
            user_id=model.user_id,
            current_balance=Decimal(model.current_balance),
            lifetime_purchased=Decimal(model.lifetime_purchased),
            lifetime_consumed=Decimal(model.lifetime_consumed),
            updated_at=model.updated_at,
        )

    def update(self, wallet: BrainWallet) -> BrainWallet:
        if wallet is None:
            raise ValueError("Brain wallet is required.")

        model = (
            self._session.query(BrainWalletModel)
            .filter(BrainWalletModel.user_id == wallet.user_id)
            .with_for_update()
            .first()
    )

        if model is None:
            raise ValueError("Brain wallet does not exist.")

        model.current_balance = wallet.current_balance
        model.lifetime_purchased = wallet.lifetime_purchased
        model.lifetime_consumed = wallet.lifetime_consumed
        model.updated_at = wallet.updated_at

        self._session.flush()

        return BrainWallet(
            user_id=model.user_id,
            current_balance=Decimal(model.current_balance),
            lifetime_purchased=Decimal(model.lifetime_purchased),
            lifetime_consumed=Decimal(model.lifetime_consumed),
            updated_at=model.updated_at,
    )
