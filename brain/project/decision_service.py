from datetime import datetime, timezone
from uuid import uuid4

from .decision_repository import ProjectDecisionRepository
from .project_decision import ProjectDecision


class ProjectDecisionService:

    VALID_STATUSES = {
        "active",
        "reversed",
        "completed",
    }

    def __init__(
        self,
        repository: ProjectDecisionRepository,
    ):
        self.repository = repository

    def create_decision(
        self,
        project_id: str,
        user_id: int,
        title: str,
        description: str | None = None,
        reason: str | None = None,
    ) -> ProjectDecision:
        if not project_id:
            raise ValueError("Project ID is required.")

        if not title or not title.strip():
            raise ValueError("Decision title is required.")

        now = datetime.now(timezone.utc)

        decision = ProjectDecision(
            decision_id=str(uuid4()),
            project_id=project_id,
            user_id=user_id,
            title=title.strip(),
            description=description.strip()
            if description
            else None,
            reason=reason.strip()
            if reason
            else None,
            status="active",
            created_at=now,
            updated_at=now,
        )

        return self.repository.create(decision)

    def get_decision(
        self,
        decision_id: str,
        user_id: int,
    ) -> ProjectDecision | None:
        return self.repository.get_by_id(
            decision_id,
            user_id,
        )

    def get_project_decisions(
        self,
        project_id: str,
        user_id: int,
    ) -> list[ProjectDecision]:
        if not project_id:
            raise ValueError("Project ID is required.")

        return self.repository.get_all(
            project_id,
            user_id,
        )

    def update_decision(
        self,
        decision_id: str,
        user_id: int,
        title: str,
        status: str,
        description: str | None = None,
        reason: str | None = None,
    ) -> ProjectDecision:
        if not title or not title.strip():
            raise ValueError("Decision title is required.")

        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid decision status: {status}"
            )

        existing = self.repository.get_by_id(
            decision_id,
            user_id,
        )

        if existing is None:
            raise ValueError("Decision not found.")

        updated_decision = ProjectDecision(
            decision_id=existing.decision_id,
            project_id=existing.project_id,
            user_id=existing.user_id,
            title=title.strip(),
            description=description.strip()
            if description
            else None,
            reason=reason.strip()
            if reason
            else None,
            status=status,
            created_at=existing.created_at,
            updated_at=datetime.now(timezone.utc),
        )

        return self.repository.update(
            updated_decision
        )

    def delete_decision(
        self,
        decision_id: str,
        user_id: int,
    ) -> None:
        existing = self.repository.get_by_id(
            decision_id,
            user_id,
        )

        if existing is None:
            raise ValueError("Decision not found.")

        self.repository.delete(
            decision_id,
            user_id,
        )