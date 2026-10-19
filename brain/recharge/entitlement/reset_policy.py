from datetime import datetime, timedelta

from brain.recharge.entitlement.models import FreeBrainEntitlement


class FreeBrainResetPolicy:
    """
    Determines whether a free Brain entitlement has reached
    its configured reset time.
    """

    def is_reset_due(
        self,
        entitlement: FreeBrainEntitlement,
        now: datetime,
    ) -> bool:
        if entitlement is None:
            raise ValueError("Free Brain entitlement is required.")

        if now is None:
            raise ValueError("Current time is required.")

        return now >= entitlement.next_reset_at

    def calculate_next_reset(
        self,
        period_started_at: datetime,
        reset_interval_hours: int,
    ) -> datetime:
        if period_started_at is None:
            raise ValueError("Period start time is required.")

        if reset_interval_hours <= 0:
            raise ValueError(
                "Reset interval must be greater than zero hours."
            )

        return period_started_at + timedelta(
            hours=reset_interval_hours
        )

    def reset(
        self,
        entitlement: FreeBrainEntitlement,
        now: datetime,
    ) -> FreeBrainEntitlement:
        if entitlement is None:
            raise ValueError("Free Brain entitlement is required.")

        if now is None:
            raise ValueError("Current time is required.")

        if not self.is_reset_due(entitlement, now):
            return entitlement

        next_reset_at = self.calculate_next_reset(
            period_started_at=now,
            reset_interval_hours=entitlement.reset_interval_hours,
        )

        return FreeBrainEntitlement(
            user_id=entitlement.user_id,
            allowance=entitlement.allowance,
            consumed=0,
            reset_interval_hours=entitlement.reset_interval_hours,
            period_started_at=now,
            next_reset_at=next_reset_at,
        )