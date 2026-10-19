from datetime import datetime, timezone
from sqlalchemy.orm import Session

from brain.subscription.models import (
    Subscription,
    SubscriptionStatus,
)
from brain.subscription.subscription_model import SubscriptionModel
from brain.tier.models import BrainTier


class SubscriptionRepository:

    def __init__(self, session: Session):
        if session is None:
            raise ValueError("Database session is required.")

        self._session = session

    def create(
        self,
        subscription: Subscription,
    ) -> Subscription:
        model = SubscriptionModel(
            user_id=subscription.user_id,
            tier=subscription.tier.value,
            status=subscription.status.value,
            started_at=subscription.started_at,
            current_period_started_at=subscription.current_period_started_at,
            current_period_ends_at=subscription.current_period_ends_at,
        )

        self._session.add(model)
        self._session.flush()

        return self._to_domain(model)

    def get_by_user_id(
        self,
        user_id: int,
        *,
        for_update: bool = False,
    ) -> Subscription | None:
        query = (
            self._session.query(SubscriptionModel)
            .filter(SubscriptionModel.user_id == user_id)
    )

        if for_update:
            query = query.with_for_update()

        model = query.first()

        if model is None:
            return None

        return self._to_domain(model)

    def update(
        self,
        subscription: Subscription,
    ) -> Subscription:
        model = (
            self._session.query(SubscriptionModel)
            .filter(
                SubscriptionModel.user_id == subscription.user_id,
            )
            .with_for_update()
            .first()
        )

        if model is None:
            raise ValueError("Subscription not found.")

        model.tier = subscription.tier.value
        model.status = subscription.status.value
        model.started_at = subscription.started_at
        model.current_period_started_at = (
            subscription.current_period_started_at
        )
        model.current_period_ends_at = (
            subscription.current_period_ends_at
        )
        model.updated_at = datetime.now(timezone.utc)

        self._session.flush()

        return self._to_domain(model)


    def _to_domain(self, model):
        return Subscription(
            user_id=model.user_id,
            tier=BrainTier(model.tier),
            status=SubscriptionStatus(model.status),

            started_at=self._ensure_utc(
                model.started_at
),
            current_period_started_at=self._ensure_utc(
                model.current_period_started_at
),
            current_period_ends_at=self._ensure_utc(
                model.current_period_ends_at
),
        )

    def _ensure_utc(self, value):
        if value is None:
            return None

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)