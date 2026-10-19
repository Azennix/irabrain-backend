from datetime import datetime
from pathlib import Path
from typing import Optional

from brain.self_development.domain.enums import DevelopmentStatus
from brain.self_development.domain.models import DevelopmentResult
from brain.self_development.development.filesystem_workspace_adapter import (
    FilesystemWorkspaceAdapter,
)

class DevelopmentExecutor:
    """
    Executes controlled development operations inside
    an isolated development workspace.

    Responsibilities:
    - verify the workspace
    - perform explicitly authorized file operations
    - return a structured development result

    It does NOT:
    - modify production files
    - execute arbitrary commands
    - deploy changes
    - release versions
    - bypass validation
    """

    def __init__(self,
        workspace_manager,
        workspace_adapter=None,
                  ):
        self.workspace_manager = workspace_manager
        self.workspace_adapter = (
            workspace_adapter
            or FilesystemWorkspaceAdapter()
        )
    def write_file(
        self,
        workspace,
        relative_path: str,
        content: str,
        improvement_id: str = "",
    ) -> DevelopmentResult:

        if workspace is None:
            raise ValueError(
                "Development workspace cannot be None."
            )

        if not relative_path.strip():
            raise ValueError(
                "File path cannot be empty."
            )

        if not isinstance(content, str):
            raise ValueError(
                "File content must be a string."
            )

        if not self.workspace_manager.exists(workspace):
            raise ValueError(
                "Development workspace does not exist."
            )

        workspace_path = Path(
            workspace.path
        ).resolve()

        target_path = (
            workspace_path / relative_path
        ).resolve()

        try:
            target_path.relative_to(
                workspace_path
            )
        except ValueError:
            raise ValueError(
                "File path escapes the development workspace."
            )

        self.workspace_adapter.write_file(
            workspace,
            relative_path,
            content,
)

        return DevelopmentResult(
            development_id=f"DEV-{workspace.workspace_id}",
            improvement_id=(
                improvement_id
                or workspace.improvement_id
            ),
            status=DevelopmentStatus.SUCCEEDED,
            workspace=workspace.path,
            changed_files=[relative_path],
            details={
                "message": (
                    f"Development file written: "
                    f"{relative_path}"
                ),
                "completed_at": datetime.utcnow().isoformat(),
            },
        )

    def read_file(
        self,
        workspace,
        relative_path: str,
    ) -> Optional[str]:

        if workspace is None:
            raise ValueError(
                "Development workspace cannot be None."
            )

        if not relative_path.strip():
            raise ValueError(
                "File path cannot be empty."
            )

        if not self.workspace_manager.exists(workspace):
            raise ValueError(
                "Development workspace does not exist."
            )

        workspace_path = Path(
            workspace.path
        ).resolve()

        target_path = (
            workspace_path / relative_path
        ).resolve()

        try:
            target_path.relative_to(
                workspace_path
            )
        except ValueError:
            raise ValueError(
                "File path escapes the development workspace."
            )

        return self.workspace_adapter.read_file(
          workspace,
          relative_path,
)