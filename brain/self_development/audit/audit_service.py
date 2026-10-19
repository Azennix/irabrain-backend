from typing import Any, Dict, Optional
from uuid import uuid4

from brain.self_development.audit.audit_event import AuditEvent
from brain.self_development.persistence.audit_event_repository import (
    AuditEventRepository,
)


class AuditService:
    def __init__(
        self,
        repository: AuditEventRepository,
    ):
        self.repository = repository

    def record(
        self,
        *,
        cycle_id: str,
        system_id: Optional[str],
        user_id: Optional[int],
        event_type: str,
        action: str,
        stage: Optional[str],
        outcome: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        event = AuditEvent(
            event_id=f"AUDIT-{uuid4().hex}",
            cycle_id=cycle_id,
            system_id=system_id,
            user_id=user_id,
            event_type=event_type,
            action=action,
            stage=stage,
            outcome=outcome,
            details=details or {},
        )

        self.repository.create(event)
        self.repository.commit()

        return event