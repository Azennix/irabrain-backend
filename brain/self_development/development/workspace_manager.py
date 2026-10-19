from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class DevelopmentWorkspace:
    """
    Represents an isolated workspace for a development attempt.
    """

    workspace_id: str
    path: str
    improvement_id: str


class WorkspaceManager:
    """
    Creates and manages isolated development workspaces.

    Responsibilities:
    - create isolated workspace directories
    - associate a workspace with an improvement
    - verify workspace existence
    - clean up a workspace

    It does NOT:
    - modify production source code
    - execute generated code
    - run tests
    - commit changes
    - deploy releases
    """

    def __init__(
        self,
        workspace_root: str = ".self_development_workspaces",
    ):
        self.workspace_root = Path(
            workspace_root
        )

    def create(
        self,
        improvement_id: str,
    ) -> DevelopmentWorkspace:

        if not improvement_id.strip():
            raise ValueError(
                "Improvement ID cannot be empty."
            )

        self.workspace_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        workspace_id = (
            f"WS-{uuid4().hex[:12]}"
        )

        workspace_path = (
            self.workspace_root / workspace_id
        )

        workspace_path.mkdir(
            parents=True,
            exist_ok=False,
        )

        return DevelopmentWorkspace(
            workspace_id=workspace_id,
            path=str(workspace_path),
            improvement_id=improvement_id,
        )

    def exists(
        self,
        workspace: DevelopmentWorkspace,
    ) -> bool:

        return Path(
            workspace.path
        ).is_dir()

    def cleanup(
        self,
        workspace: DevelopmentWorkspace,
    ) -> None:

        path = Path(workspace.path)

        if not path.exists():
            return

        if not path.is_dir():
            raise ValueError(
                "Workspace path is not a directory."
            )

        for child in path.iterdir():

            if child.is_dir():
                self._remove_directory(child)
            else:
                child.unlink()

        path.rmdir()

    def _remove_directory(
        self,
        path: Path,
    ) -> None:

        for child in path.iterdir():

            if child.is_dir():
                self._remove_directory(child)
            else:
                child.unlink()

        path.rmdir()