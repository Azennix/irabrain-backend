from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass(frozen=True)
class Version:
    """
    Represents a version of IRABRAIN.
    """

    version: str
    parent_version: Optional[str]
    source_reference: str
    description: str
    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


class VersionManager:
    """
    Manages logical IRABRAIN versions.

    Responsibilities:
    - create versions
    - track parent versions
    - associate versions with source references
    - retrieve versions
    - expose version history

    It does NOT:
    - modify source code
    - perform Git operations
    - deploy versions
    - decide whether a version is releasable
    """

    def __init__(
        self,
        initial_version: str = "V1.0.0",
    ):
        if not initial_version.strip():
            raise ValueError(
                "Initial version cannot be empty."
            )

        self._versions: Dict[str, Version] = {}

        self._versions[initial_version] = Version(
            version=initial_version,
            parent_version=None,
            source_reference="initial",
            description="Initial IRABRAIN foundation.",
        )

    def create_version(
        self,
        version: str,
        source_reference: str,
        description: str,
        parent_version: Optional[str] = None,
    ) -> Version:

        if not version.strip():
            raise ValueError(
                "Version cannot be empty."
            )

        if not source_reference.strip():
            raise ValueError(
                "Source reference cannot be empty."
            )

        if not description.strip():
            raise ValueError(
                "Version description cannot be empty."
            )

        if version in self._versions:
            raise ValueError(
                f"Version already exists: {version}"
            )

        if (
            parent_version is not None
            and parent_version not in self._versions
        ):
            raise ValueError(
                f"Parent version not found: "
                f"{parent_version}"
            )

        created = Version(
            version=version,
            parent_version=parent_version,
            source_reference=source_reference,
            description=description,
        )

        self._versions[version] = created

        return created

    def get(
        self,
        version: str,
    ) -> Optional[Version]:

        return self._versions.get(version)

    def exists(
        self,
        version: str,
    ) -> bool:

        return version in self._versions

    def history(self):

        return list(self._versions.values())