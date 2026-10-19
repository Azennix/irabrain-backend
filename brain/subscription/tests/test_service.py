from datetime import datetime, timedelta, timezone

from brain.subscription.models import SubscriptionStatus
from brain.subscription.repository import SubscriptionRepository
from brain.subscription.service import SubscriptionService
from brain.tier.models import BrainTier
from database.database import SessionLocal


def test_subscription_service_activate_get_cancel():
    user_id = 999975

    session = SessionLocal()

    try:
        repository = SubscriptionRepository(session)
        service = SubscriptionService(repository=repository)

        started_at = datetime.now(timezone.utc)
        period_ends_at = started_at + timedelta(days=30)

        activated = service.activate(
            user_id=user_id,
            tier=BrainTier.THALAMUS,
            started_at=started_at,
            current_period_started_at=started_at,
            current_period_ends_at=period_ends_at,
        )

        assert activated.user_id == user_id
        assert activated.tier == BrainTier.THALAMUS
        assert activated.status == SubscriptionStatus.ACTIVE

        session.commit()

        fetched = service.get_subscription(user_id)

        assert fetched is not None
        assert fetched.status == SubscriptionStatus.ACTIVE

        cancelled = service.cancel(user_id)

        assert cancelled.user_id == user_id
        assert cancelled.status == SubscriptionStatus.CANCELLED

        session.commit()

        final = service.get_subscription(user_id)

        assert final is not None
        assert final.status == SubscriptionStatus.CANCELLED

    finally:
        session.rollback()
        session.close()