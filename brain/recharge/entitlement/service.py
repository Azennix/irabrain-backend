from datetime import datetime
from decimal import Decimal

from brain.recharge.entitlement.models import FreeBrainEntitlement
from brain.recharge.entitlement.repository import (
    FreeBrainEntitlementRepository,
)
from brain.recharge.entitlement.reset_policy import (
    FreeBrainResetPolicy,
)
from brain.recharge.entitlement.consumption import (
    FreeBrainConsumptionPolicy,
)


class FreeBrainEntitlementService:
    def __init__(
        self,
        repository: FreeBrainEntitlementRepository,
        reset_policy: FreeBrainResetPolicy,
        consumption_policy: FreeBrainConsumptionPolicy,

    ):
        if repository is None:
            raise ValueError("Entitlement repository is required.")

        if reset_policy is None:
            raise ValueError("Free Brain reset policy is required.")

        if consumption_policy is None:
            raise ValueError("Free Brain consumption policy is required.")

        self._repository = repository
        self._reset_policy = reset_policy
        self._consumption_policy = consumption_policy

    def get_or_create(
        self,
        user_id: int,
        allowance: Decimal,
        reset_interval_hours: int,
        now: datetime,
    ) -> FreeBrainEntitlement:
        if user_id <= 0:
            raise ValueError("User ID must be greater than zero.")

        if allowance <= 0:
            raise ValueError(
                "Free Brain allowance must be greater than zero."
            )

        if reset_interval_hours <= 0:
            raise ValueError(
                "Reset interval must be greater than zero hours."
            )

        if now is None:
            raise ValueError("Current time is required.")

        entitlement = self._repository.get(user_id)

        if entitlement is not None:
            return self._apply_reset_if_due(
                entitlement=entitlement,
                now=now,
            )

        next_reset_at = self._reset_policy.calculate_next_reset(
            period_started_at=now,
            reset_interval_hours=reset_interval_hours,
        )

        entitlement = FreeBrainEntitlement(
            user_id=user_id,
            allowance=allowance,
            consumed=Decimal("0"),
            reset_interval_hours=reset_interval_hours,
            period_started_at=now,
            next_reset_at=next_reset_at,
        )

        self._repository.create(entitlement)

        return entitlement

    def refresh(
        self,
        user_id: int,
        now: datetime,
    ) -> FreeBrainEntitlement:
        if user_id <= 0:
            raise ValueError("User ID must be greater than zero.")

        if now is None:
            raise ValueError("Current time is required.")

        entitlement = self._repository.get(user_id)

        if entitlement is None:
            raise ValueError(
                "Free Brain entitlement does not exist."
            )

        return self._apply_reset_if_due(
            entitlement=entitlement,
            now=now,
        )

    def get_current(
        self,
        user_id: int,
        now: datetime,
    ) -> FreeBrainEntitlement | None:
        if user_id <= 0:
            raise ValueError(
                "User ID must be greater than zero."
        )

        if now is None:
            raise ValueError("Current time is required.")

        entitlement = self._repository.get(user_id)

        if entitlement is None:
            return None

        return self._apply_reset_if_due(
            entitlement=entitlement,
            now=now,
    )




    def consume(
        self,
        user_id: int,
        requested_units: Decimal,
        now: datetime,
    ) -> tuple[FreeBrainEntitlement, Decimal, bool]:
        if user_id <= 0:
            raise ValueError("User ID must be greater than zero.")

        if requested_units <= 0:
            raise ValueError(
                "Requested Brain Units must be greater than zero."
        )

        if now is None:
            raise ValueError("Current time is required.")

        entitlement = self._repository.get(user_id)

        if entitlement is None:
            raise ValueError(
                "Free Brain entitlement does not exist."
        )

        entitlement = self._apply_reset_if_due(
            entitlement=entitlement,
            now=now,
    )

        result = self._consumption_policy.calculate(
            entitlement=entitlement,
            requested_units=requested_units,
    )

        if result.consumed <= 0:
            return (
                entitlement,
                Decimal("0"),
                False,
        )

        updated_entitlement = FreeBrainEntitlement(
            user_id=entitlement.user_id,
            allowance=entitlement.allowance,
            consumed=entitlement.consumed + result.consumed,
            reset_interval_hours=entitlement.reset_interval_hours,
            period_started_at=entitlement.period_started_at,
            next_reset_at=entitlement.next_reset_at,
    )

        self._repository.update(updated_entitlement)

        return (
            updated_entitlement,
            result.consumed,
            result.fully_consumed,
    )

    def _apply_reset_if_due(
        self,
        entitlement: FreeBrainEntitlement,
        now: datetime,
    ) -> FreeBrainEntitlement:
        if not self._reset_policy.is_reset_due(
            entitlement=entitlement,
            now=now,
        ):
            return entitlement

        reset_entitlement = self._reset_policy.reset(
            entitlement=entitlement,
            now=now,
        )

        self._repository.update(reset_entitlement)

        return reset_entitlement
    def commit(self):
        self._repository.commit()

    