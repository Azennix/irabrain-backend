from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(frozen=True, slots=True)
class ExecutionCost:
    amount: Decimal
    currency: str
    source: str
    version: str
    metadata: dict[str, Any] = field(default_factory=dict)