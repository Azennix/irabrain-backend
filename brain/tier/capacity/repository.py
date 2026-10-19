from datetime import datetime, timezone
from decimal import Decimal

from brain.tier.capacity.models import TierBrainCapacity
from brain.tier.capacity.capacity_model import TierBrainCapacityModel
from brain.tier.models import BrainTier


class TierBrainCapacityRepository:
    def __init__(self, session):
        if session is None:
            raise ValueError("Database session is required.")

        self._session = session

    def get(
        self,
        user_id: int,
    ) -> TierBrainCapacity | None:
        model = (
            self._session.query(TierBrainCapacityModel)
            .filter(
                TierBrainCapacityModel.user_id == user_id
            )
            .with_for_update()
            .first()
        )

        if model is None:
            return None

        return TierBrainCapacity(
            user_id=model.user_id,
            tier=BrainTier(model.tier),
            allowance=Decimal(model.allowance),
            consumed=Decimal(model.consumed),
            period_started_at=self._ensure_utc(
                model.period_started_at
            ),
            period_ends_at=self._ensure_utc(
                model.period_ends_at
            ),
        )

    def _ensure_utc(self, value):
        if value is None:
            return None

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    def create(
        self,
        capacity: TierBrainCapacity,
    ) -> TierBrainCapacity:
        if capacity is None:
            raise ValueError(
                "Tier Brain capacity is required."
            )

        model = TierBrainCapacityModel(
            user_id=capacity.user_id,
            tier=capacity.tier.value,
            allowance=capacity.allowance,
            consumed=capacity.consumed,
            period_started_at=self._ensure_utc(
                capacity.period_started_at
            ),
            period_ends_at=self._ensure_utc(
                capacity.period_ends_at
            ),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self._session.add(model)
        self._session.flush()

        return capacity

    def update(
        self,
        capacity: TierBrainCapacity,
    ) -> TierBrainCapacity:
        if capacity is None:
            raise ValueError(
                "Tier Brain capacity is required."
            )

        model = (
            self._session.query(TierBrainCapacityModel)
            .filter(
                TierBrainCapacityModel.user_id
                == capacity.user_id
            )
            .with_for_update()
            .first()
        )

        if model is None:
            raise ValueError(
                "Tier Brain capacity does not exist."
            )

        model.tier = capacity.tier.value
        model.allowance = capacity.allowance
        model.consumed = capacity.consumed
        model.period_started_at = (
            capacity.period_started_at
        )
        model.period_ends_at = (
            capacity.period_ends_at
        )
        model.updated_at = datetime.now(timezone.utc)

        self._session.flush()

        return capacity