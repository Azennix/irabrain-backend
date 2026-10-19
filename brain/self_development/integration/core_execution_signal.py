from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class CoreExecutionSignal:
    """
    Immutable signal emitted by IRABRAIN Core.

    This is a communication contract between
    IRABRAIN Core and the separate Self-Development system.

    It carries execution information only.
    It does not grant control or authorization.
    """

    signal_id: str
    operation: str
    success: bool

    execution_time: float

    metadata: dict[str, Any] = field(default_factory=dict)

    error: str | None = None

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )