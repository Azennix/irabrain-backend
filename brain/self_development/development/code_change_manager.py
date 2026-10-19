from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from brain.self_development.policy.change_policy import (
    ChangePolicy,
)


@dataclass(frozen=True)
class FileChange:
    path: str
    operation: str
    description: str


@dataclass(frozen=True)
class CodeChangeSet:
    change_id: str
    improvement_id: str
    changes: List[FileChange]
    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


class CodeChangeManager:
    """
    Manages structured code-change proposals.

    Responsibilities:
    - create change sets
    - validate requested file operations
    - keep changes associated with an improvement
    - provide a traceable change description

    It does NOT:
    - modify production code
    - execute arbitrary commands
    - run tests
    - commit changes
    - deploy releases
    """

    def __init__(
        self,
        change_policy: ChangePolicy | None = None,
):
        self._change_sets = {}
        self._counter = 0
        self.change_policy = (
            change_policy
            or ChangePolicy()
    )

    def create_change_set(
        self,
        improvement_id: str,
        changes: List[FileChange],
    ) -> CodeChangeSet:

        if not improvement_id.strip():
            raise ValueError(
                "Improvement ID cannot be empty."
            )

        if not changes:
            raise ValueError(
                "At least one file change is required."
            )

        for change in changes:
            if not change.path.strip():
                raise ValueError(
                    "Change file path cannot be empty."
                )

        if not self.change_policy.can_change(
            operation=change.operation,
            path=change.path,
):
            raise ValueError(
                f"Change blocked by policy: "
                f"{change.operation} -> {change.path}"
    )

        self._counter += 1

        change_id = (
            f"CHG-{self._counter:04d}"
        )

        change_set = CodeChangeSet(
            change_id=change_id,
            improvement_id=improvement_id,
            changes=list(changes),
        )

        self._change_sets[change_id] = change_set

        return change_set

    def get(
        self,
        change_id: str,
    ) -> CodeChangeSet | None:

        return self._change_sets.get(
            change_id
        )

    def list_for_improvement(
        self,
        improvement_id: str,
    ) -> List[CodeChangeSet]:

        return [
            change_set
            for change_set in self._change_sets.values()
            if change_set.improvement_id == improvement_id
        ]