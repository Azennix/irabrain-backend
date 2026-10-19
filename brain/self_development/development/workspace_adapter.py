from abc import ABC, abstractmethod
from typing import Optional


class WorkspaceAdapter(ABC):
    """
    Boundary between the development executor and
    the underlying development workspace.

    Implementations are responsible only for controlled
    workspace file operations.
    """

    @abstractmethod
    def write_file(
        self,
        workspace,
        relative_path: str,
        content: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_file(
        self,
        workspace,
        relative_path: str,
    ) -> Optional[str]:
        raise NotImplementedError