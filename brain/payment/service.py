from datetime import datetime, timezone
from decimal import Decimal

from brain.payment.models import Payment, PaymentStatus
from brain.payment.repository import PaymentRepository
from brain.payment.providers.base import PaymentProvider
from brain.tier.models import BrainTier


class PaymentService:

    def __init__(
        self,
        payment_repository: PaymentRepository,
        payment_provider: PaymentProvider,
    ):
        if payment_repository is None:
            raise ValueError("Payment repository is required.")

        if payment_provider is None:
            raise ValueError("Payment provider is required.")

        self._payment_repository = payment_repository
        self._payment_provider = payment_provider

    def create_payment(
        self,
        *,
        user_id: int,
        tier: BrainTier,
        amount: Decimal,
        currency: str,
    ) -> Payment:

        order = self._payment_provider.create_order(
            user_id=user_id,
            tier=tier,
            amount=amount,
            currency=currency,
        )

        now = datetime.now(timezone.utc)

        payment = Payment(
            payment_id=None,
            user_id=user_id,
            tier=tier,
            amount=amount,
            currency=currency,
            status=PaymentStatus.CREATED,
            provider=order.provider,
            provider_order_id=order.provider_order_id,
            provider_payment_id=None,
            created_at=now,
            updated_at=now,
        )

        return self._payment_repository.create(payment)