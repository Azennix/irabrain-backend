from typing import List, Optional

from brain.self_development.audit.audit_event import AuditEvent
from brain.self_development.persistence.audit_event_model import (
    AuditEventModel,
)


class AuditEventRepository:
    def __init__(self, db):
        self.db = db

    def create(self, event: AuditEvent) -> AuditEvent:
        model = AuditEventModel(
            event_id=event.event_id,
            cycle_id=event.cycle_id,
            system_id=event.system_id,
            user_id=event.user_id,
            event_type=event.event_type,
            action=event.action,
            stage=event.stage,
            outcome=event.outcome,
            details=event.details,
            created_at=event.created_at,
        )

        self.db.add(model)
        self.db.flush()

        return event

    def get_by_id(
        self,
        event_id: str,
    ) -> Optional[AuditEventModel]:
        return self.db.get(
            AuditEventModel,
            event_id,
        )

    def list_by_cycle(
        self,
        cycle_id: str,
    ) -> List[AuditEventModel]:
        return (
            self.db.query(AuditEventModel)
            .filter(
                AuditEventModel.cycle_id == cycle_id
            )
            .order_by(
                AuditEventModel.created_at.asc()
            )
            .all()
        )

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()