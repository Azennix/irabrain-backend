from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class RepositoryFile:
    path: str
    file_type: str
    size_bytes: int


@dataclass
class RepositorySnapshot:
    root: str
    files: List[RepositoryFile] = field(
        default_factory=list
    )


class RepositoryAnalyzer:
    """
    Analyzes the structure of the IRABRAIN repository.

    Responsibilities:
    - inspect repository files
    - identify file types
    - record basic repository structure
    - produce a repository snapshot

    It does NOT:
    - modify files
    - execute source code
    - change the repository
    - commit changes
    - deploy anything
    """

    def analyze(
        self,
        repository_root: str,
    ) -> RepositorySnapshot:

        root = Path(repository_root)

        if not root.exists():
            raise ValueError(
                f"Repository does not exist: {repository_root}"
            )

        if not root.is_dir():
            raise ValueError(
                f"Repository root is not a directory: {repository_root}"
            )

        files = []

        for path in root.rglob("*"):

            if not path.is_file():
                continue

            try:
                relative_path = path.relative_to(root)
                size_bytes = path.stat().st_size
            except OSError:
                continue

            suffix = path.suffix.lower()

            file_type = (
                suffix[1:]
                if suffix
                else "unknown"
            )

            files.append(
                RepositoryFile(
                    path=str(relative_path),
                    file_type=file_type,
                    size_bytes=size_bytes,
                )
            )

        files.sort(
            key=lambda item: item.path
        )

        return RepositorySnapshot(
            root=str(root),
            files=files,
        )