from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass(frozen=True, slots=True)
class BrainWallet:
    user_id: int
    current_balance: Decimal
    lifetime_purchased: Decimal
    lifetime_consumed: Decimal
    updated_at: datetime