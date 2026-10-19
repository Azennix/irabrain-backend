from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class VersionRecord:
    """
    Registry record for an IRABRAIN version.
    """

    version: str
    status: str
    source_reference: str


class VersionRegistry:
    """
    Stores the known state of IRABRAIN versions.

    Responsibilities:
    - register versions
    - update version status
    - retrieve version records
    - identify the current version
    - identify known-good versions

    It does NOT:
    - modify source code
    - perform Git operations
    - deploy versions
    - make release decisions
    """

    def __init__(self):
        self._versions: Dict[str, VersionRecord] = {}
        self._current_version: Optional[str] = None
        self._known_good_version: Optional[str] = None

    def register(
        self,
        version: str,
        status: str,
        source_reference: str,
    ) -> VersionRecord:

        if not version.strip():
            raise ValueError(
                "Version cannot be empty."
            )

        if not status.strip():
            raise ValueError(
                "Version status cannot be empty."
            )

        if not source_reference.strip():
            raise ValueError(
                "Source reference cannot be empty."
            )

        if version in self._versions:
            raise ValueError(
                f"Version already registered: {version}"
            )

        record = VersionRecord(
            version=version,
            status=status,
            source_reference=source_reference,
        )

        self._versions[version] = record

        return record

    def set_current(
        self,
        version: str,
    ) -> None:

        if version not in self._versions:
            raise ValueError(
                f"Version not registered: {version}"
            )

        self._current_version = version

    def set_known_good(
        self,
        version: str,
    ) -> None:

        if version not in self._versions:
            raise ValueError(
                f"Version not registered: {version}"
            )

        self._known_good_version = version

    def get(
        self,
        version: str,
    ) -> Optional[VersionRecord]:

        return self._versions.get(version)

    def get_current(
        self,
    ) -> Optional[VersionRecord]:

        if self._current_version is None:
            return None

        return self.get(
            self._current_version
        )

    def get_known_good(
        self,
    ) -> Optional[VersionRecord]:

        if self._known_good_version is None:
            return None

        return self.get(
            self._known_good_version
        )

    def history(self):

        return list(self._versions.values())