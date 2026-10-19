from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any


class BrainTransactionType(str, Enum):
    RECHARGE = "recharge"
    TASK_CONSUMPTION = "task_consumption"
    REFUND = "refund"
    PROMOTIONAL_CREDIT = "promotional_credit"
    ADJUSTMENT = "adjustment"
    EXPIRATION = "expiration"

class BrainTransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass(frozen=True, slots=True)
class BrainTransaction:
    transaction_id: str
    user_id: int
    transaction_type: BrainTransactionType
    units: Decimal
    reference_id: str | None
    status: BrainTransactionStatus
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)