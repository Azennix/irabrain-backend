from pathlib import Path
from typing import Optional

from brain.self_development.development.workspace_adapter import (
    WorkspaceAdapter,
)


class FilesystemWorkspaceAdapter(WorkspaceAdapter):
    """
    Controlled filesystem implementation of WorkspaceAdapter.

    All file operations are restricted to the supplied
    development workspace.
    """

    def write_file(
        self,
        workspace,
        relative_path: str,
        content: str,
    ) -> None:

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

        target_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target_path.write_text(
            content,
            encoding="utf-8",
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

        if not target_path.is_file():
            return None

        return target_path.read_text(
            encoding="utf-8"
        )