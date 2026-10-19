from datetime import datetime, timezone

from sqlalchemy.orm import Session

from database.models import ProjectDecisionEntity

from .decision_repository import ProjectDecisionRepository
from .project_decision import ProjectDecision


class SqlAlchemyProjectDecisionRepository(
    ProjectDecisionRepository
):

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(
        entity: ProjectDecisionEntity,
    ) -> ProjectDecision:
        return ProjectDecision(
            decision_id=entity.decision_id,
            project_id=entity.project_id,
            user_id=entity.user_id,
            title=entity.title,
            description=entity.description,
            reason=entity.reason,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def create(
        self,
        decision: ProjectDecision,
    ) -> ProjectDecision:
        entity = ProjectDecisionEntity(
            decision_id=decision.decision_id,
            project_id=decision.project_id,
            user_id=decision.user_id,
            title=decision.title,
            description=decision.description,
            reason=decision.reason,
            status=decision.status,
            created_at=decision.created_at,
            updated_at=decision.updated_at,
        )

        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)

        return self._to_domain(entity)

    def get_by_id(
        self,
        decision_id: str,
        user_id: int,
    ) -> ProjectDecision | None:
        entity = (
            self.db.query(ProjectDecisionEntity)
            .filter(
                ProjectDecisionEntity.decision_id == decision_id,
                ProjectDecisionEntity.user_id == user_id,
            )
            .first()
        )

        if entity is None:
            return None

        return self._to_domain(entity)

    def get_all(
        self,
        project_id: str,
        user_id: int,
    ) -> list[ProjectDecision]:
        entities = (
            self.db.query(ProjectDecisionEntity)
            .filter(
                ProjectDecisionEntity.project_id == project_id,
                ProjectDecisionEntity.user_id == user_id,
            )
            .order_by(ProjectDecisionEntity.created_at.desc())
            .all()
        )

        return [
            self._to_domain(entity)
            for entity in entities
        ]

    def update(
        self,
        decision: ProjectDecision,
    ) -> ProjectDecision:
        entity = (
            self.db.query(ProjectDecisionEntity)
            .filter(
                ProjectDecisionEntity.decision_id
                == decision.decision_id,
                ProjectDecisionEntity.user_id
                == decision.user_id,
            )
            .first()
        )

        if entity is None:
            raise ValueError("Decision not found.")

        entity.project_id = decision.project_id
        entity.title = decision.title
        entity.description = decision.description
        entity.reason = decision.reason
        entity.status = decision.status
        entity.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(entity)

        return self._to_domain(entity)

    def delete(
        self,
        decision_id: str,
        user_id: int,
    ) -> None:
        entity = (
            self.db.query(ProjectDecisionEntity)
            .filter(
                ProjectDecisionEntity.decision_id == decision_id,
                ProjectDecisionEntity.user_id == user_id,
            )
            .first()
        )

        if entity is None:
            raise ValueError("Decision not found.")

        self.db.delete(entity)
        self.db.commit()