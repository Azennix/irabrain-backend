from datetime import datetime, timezone

from sqlalchemy.orm import Session

from brain.payment.models import Payment, PaymentStatus
from brain.payment.payment_model import PaymentModel
from brain.tier.models import BrainTier


class PaymentRepository:

    def __init__(self, session: Session):
        if session is None:
            raise ValueError("Database session is required.")

        self._session = session

    def create(
        self,
        payment: Payment,
    ) -> Payment:
        model = PaymentModel(
            user_id=payment.user_id,
            tier=payment.tier.value,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status.value,
            provider=payment.provider,
            provider_order_id=payment.provider_order_id,
            provider_payment_id=payment.provider_payment_id,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )

        self._session.add(model)
        self._session.flush()

        return self._to_domain(model)

    def get_by_id(
        self,
        payment_id: int,
        *,
        for_update: bool = False,
    ) -> Payment | None:
        query = (
            self._session.query(PaymentModel)
            .filter(
                PaymentModel.payment_id == payment_id,
        )
    )

        if for_update:
            query = query.with_for_update()

        model = query.first()

        if model is None:
            return None

        return self._to_domain(model)

    def get_by_provider_payment_id(
        self,
        provider_payment_id: str,
    ) -> Payment | None:
        model = (
            self._session.query(PaymentModel)
            .filter(
                PaymentModel.provider_payment_id
                == provider_payment_id,
            )
            .first()
        )

        if model is None:
            return None

        return self._to_domain(model)

    def get_by_user_id(
        self,
        user_id: int,
    ) -> list[Payment]:
        models = (
            self._session.query(PaymentModel)
            .filter(
                PaymentModel.user_id == user_id,
            )
            .order_by(
                PaymentModel.created_at.desc(),
            )
            .all()
        )

        return [
            self._to_domain(model)
            for model in models
        ]

    def update(
        self,
        payment: Payment,
    ) -> Payment:
        model = (
            self._session.query(PaymentModel)
            .filter(
                PaymentModel.payment_id
                == payment.payment_id
            )
            .first()
        )

        if model is None:
            raise ValueError("Payment not found.")

        model.tier = payment.tier.value
        model.amount = payment.amount
        model.currency = payment.currency
        model.status = payment.status.value
        model.provider = payment.provider
        model.provider_order_id = payment.provider_order_id
        model.provider_payment_id = (
            payment.provider_payment_id
        )
        model.updated_at = datetime.now(timezone.utc)

        self._session.flush()

        return self._to_domain(model)

    def _to_domain(
        self,
        model,
    ) -> Payment:
        return Payment(
            payment_id=model.payment_id,
            user_id=model.user_id,
            tier=BrainTier(model.tier),
            amount=model.amount,
            currency=model.currency,
            status=PaymentStatus(model.status),
            provider=model.provider,
            provider_order_id=model.provider_order_id,
            provider_payment_id=model.provider_payment_id,
            created_at=self._ensure_utc(
                model.created_at
            ),
            updated_at=self._ensure_utc(
                model.updated_at
            ),
        )

    def _ensure_utc(
        self,
        value,
    ):
        if value is None:
            return None

        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(timezone.utc)