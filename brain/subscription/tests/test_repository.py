from datetime import datetime, timedelta, timezone

from brain.subscription.models import (
    Subscription,
    SubscriptionStatus,
)
from brain.subscription.repository import SubscriptionRepository
from brain.tier.models import BrainTier
from database.database import SessionLocal


def test_subscription_repository_create_get_update():
    user_id = 999974

    session = SessionLocal()

    try:
        repository = SubscriptionRepository(session)

        started_at = datetime.now(timezone.utc)
        period_ends_at = started_at + timedelta(days=30)

        subscription = Subscription(
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            status=SubscriptionStatus.ACTIVE,
            started_at=started_at,
            current_period_started_at=started_at,
            current_period_ends_at=period_ends_at,
        )

        created = repository.create(subscription)

        assert created.user_id == user_id
        assert created.tier == BrainTier.THALAMUS
        assert created.status == SubscriptionStatus.ACTIVE

        session.commit()

        fetched = repository.get_by_user_id(user_id)

        assert fetched is not None
        assert fetched.user_id == user_id
        assert fetched.tier == BrainTier.THALAMUS
        assert fetched.status == SubscriptionStatus.ACTIVE

        updated = Subscription(
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            status=SubscriptionStatus.CANCELLED,
            started_at=started_at,
            current_period_started_at=started_at,
            current_period_ends_at=period_ends_at,
        )

        result = repository.update(updated)

        assert result.status == SubscriptionStatus.CANCELLED

        session.commit()

        fetched_again = repository.get_by_user_id(user_id)

        assert fetched_again is not None
        assert fetched_again.status == SubscriptionStatus.CANCELLED

    finally:
        session.rollback()
        session.close()