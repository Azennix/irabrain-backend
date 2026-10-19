from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class GitChange:
    """
    Represents a Git operation requested by the
    self-development pipeline.
    """

    operation: str
    description: str


@dataclass(frozen=True)
class GitOperationResult:
    """
    Result of a Git operation.
    """

    success: bool
    workspace_id: str
    operation: str
    message: str
    completed_at: datetime = field(
        default_factory=datetime.utcnow
    )


class GitManager:
    """
    Provides a controlled abstraction around Git operations.

    Responsibilities:
    - register Git operations
    - validate requested operations
    - keep operations associated with a workspace
    - provide traceable operation results

    It does NOT:
    - push arbitrary changes to remote repositories
    - deploy production code
    - bypass release policy
    - execute unrestricted shell commands
    """

    ALLOWED_OPERATIONS = {
        "status",
        "diff",
        "commit",
        "branch",
    }

    def __init__(self):
        self._operations: List[GitChange] = []

    def execute(
        self,
        workspace_id: str,
        operation: str,
        description: str,
    ) -> GitOperationResult:

        if not workspace_id.strip():
            raise ValueError(
                "Workspace ID cannot be empty."
            )

        if operation not in self.ALLOWED_OPERATIONS:
            raise ValueError(
                f"Unsupported Git operation: {operation}"
            )

        if not description.strip():
            raise ValueError(
                "Git operation description cannot be empty."
            )

        change = GitChange(
            operation=operation,
            description=description,
        )

        self._operations.append(change)

        return GitOperationResult(
            success=True,
            workspace_id=workspace_id,
            operation=operation,
            message=(
                f"Git operation registered: {operation}"
            ),
        )

    def history(self) -> List[GitChange]:
        """
        Return the registered Git operation history.
        """

        return list(self._operations)