from datetime import datetime, timezone
from decimal import Decimal

from brain.recharge.entitlement.models import FreeBrainEntitlement
from brain.recharge.entitlement.entitlement_model import (
    FreeBrainEntitlementModel,
)


class FreeBrainEntitlementRepository:
    def __init__(self, session):
        if session is None:
            raise ValueError("Database session is required.")

        self._session = session

    def get(
        self,
        user_id: int,
    ) -> FreeBrainEntitlement | None:
        model = (
            self._session.query(FreeBrainEntitlementModel)
            .filter(
                FreeBrainEntitlementModel.user_id == user_id
            )
            .with_for_update()
            .first()
        )

        if model is None:
            return None

        return FreeBrainEntitlement(
            user_id=model.user_id,
            allowance=Decimal(model.allowance),
            consumed=Decimal(model.consumed),
            reset_interval_hours=model.reset_interval_hours,
            period_started_at=self._ensure_utc(model.period_started_at),
            next_reset_at=self._ensure_utc(model.next_reset_at),
        )
    def _ensure_utc(self, value):
        if value is None:
            return None

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    def create(
        self,
        entitlement: FreeBrainEntitlement,
    ) -> FreeBrainEntitlement:
        if entitlement is None:
            raise ValueError(
                "Free Brain entitlement is required."
            )

        model = FreeBrainEntitlementModel(
            user_id=entitlement.user_id,
            allowance=entitlement.allowance,
            consumed=entitlement.consumed,
            reset_interval_hours=entitlement.reset_interval_hours,
            period_started_at=self._ensure_utc(entitlement.period_started_at),
            next_reset_at=entitlement.next_reset_at,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self._session.add(model)
        self._session.flush()

        return entitlement

    def update(
        self,
        entitlement: FreeBrainEntitlement,
    ) -> FreeBrainEntitlement:
        if entitlement is None:
            raise ValueError(
                "Free Brain entitlement is required."
            )

        model = (
            self._session.query(FreeBrainEntitlementModel)
            .filter(
                FreeBrainEntitlementModel.user_id
                == entitlement.user_id
            )
            .with_for_update()
            .first()
        )

        if model is None:
            raise ValueError(
                "Free Brain entitlement does not exist."
            )

        model.allowance = entitlement.allowance
        model.consumed = entitlement.consumed
        model.reset_interval_hours = (
            entitlement.reset_interval_hours
        )
        model.period_started_at = (
            entitlement.period_started_at
        )
        model.next_reset_at = entitlement.next_reset_at
        model.updated_at = datetime.now(timezone.utc)

        self._session.flush()

        return entitlement
    
    def commit(self):
        self._session.commit()        # CORRECT
       
  