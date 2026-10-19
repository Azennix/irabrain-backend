from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class FreeBrainEntitlement:
    """
    Defines a user's free Brain allowance and its reset window.

    The reset window is configurable so the product can support
    different durations without changing the entitlement architecture.
    """

    user_id: int
    allowance: Decimal
    consumed: Decimal
    reset_interval_hours: int
    period_started_at: datetime
    next_reset_at: datetime