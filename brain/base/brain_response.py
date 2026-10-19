from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class BrainResponse:
    """
    Standard response object returned by every IRABRAIN engine.
    """

    success: bool = True

    data: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    execution_time: float = 0.0

    timestamp: datetime = field(default_factory=datetime.utcnow)