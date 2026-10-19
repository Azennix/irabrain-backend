from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    cycle_id: str
    system_id: Optional[str]
    user_id: Optional[int]
    event_type: str
    action: str
    stage: Optional[str]
    outcome: str
    details: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id is required.")

        if not self.cycle_id.strip():
            raise ValueError("cycle_id is required.")

        if not self.event_type.strip():
            raise ValueError("event_type is required.")

        if not self.action.strip():
            raise ValueError("action is required.")

        if not self.outcome.strip():
            raise ValueError("outcome is required.")

        if self.system_id is not None and self.user_id is not None:
            raise ValueError(
                "An audit event cannot belong to both a human and a system."
            )

        if self.system_id is None and self.user_id is None:
            raise ValueError(
                "An audit event requires either a human or system owner."
            )