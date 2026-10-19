from datetime import datetime
from decimal import Decimal

import pytest

from brain.recharge.wallet.models import BrainWallet
from brain.recharge.wallet.service import BrainWalletService


def create_wallet() -> BrainWallet:
    return BrainWallet(
        user_id=1,
        current_balance=Decimal("100"),
        lifetime_purchased=Decimal("100"),
        lifetime_consumed=Decimal("0"),
        updated_at=datetime.utcnow(),
    )


def test_wallet_recharge():
    service = BrainWalletService()
    wallet = create_wallet()

    updated = service.recharge(
        wallet,
        Decimal("50"),
    )

    assert updated.current_balance == Decimal("150")
    assert updated.lifetime_purchased == Decimal("150")
    assert updated.lifetime_consumed == Decimal("0")


def test_wallet_consumption():
    service = BrainWalletService()
    wallet = create_wallet()

    updated = service.consume(
        wallet,
        Decimal("30"),
    )

    assert updated.current_balance == Decimal("70")
    assert updated.lifetime_purchased == Decimal("100")
    assert updated.lifetime_consumed == Decimal("30")


def test_wallet_rejects_insufficient_balance():
    service = BrainWalletService()
    wallet = create_wallet()

    with pytest.raises(ValueError, match="Insufficient Brain Balance"):
        service.consume(
            wallet,
            Decimal("150"),
        )


def test_wallet_rejects_zero_or_negative_recharge():
    service = BrainWalletService()
    wallet = create_wallet()

    with pytest.raises(ValueError):
        service.recharge(wallet, Decimal("0"))

    with pytest.raises(ValueError):
        service.recharge(wallet, Decimal("-10"))


def test_wallet_rejects_zero_or_negative_consumption():
    service = BrainWalletService()
    wallet = create_wallet()

    with pytest.raises(ValueError):
        service.consume(wallet, Decimal("0"))

    with pytest.raises(ValueError):
        service.consume(wallet, Decimal("-10"))