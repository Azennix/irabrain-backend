from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class ChangePolicy:
    """
    Defines boundaries for self-development code changes.

    This policy does not perform changes.
    It only determines whether a requested
    change operation is allowed.
    """

    allowed_operations: Set[str] = field(
        default_factory=lambda: {
            "create",
            "modify",
            "test",
            "validate",
        }
    )

    blocked_operations: Set[str] = field(
        default_factory=lambda: {
            "delete_core_system",
            "disable_security",
            "modify_credentials",
            "modify_secrets",
            "unrestricted_production_change",
        }
    )

    protected_paths: Set[str] = field(
        default_factory=lambda: {
            ".env",
            "credentials",
            "secrets",
        }
    )

    def is_operation_allowed(
        self,
        operation: str,
    ) -> bool:

        if not operation.strip():
            raise ValueError(
                "Operation cannot be empty."
            )

        if operation in self.blocked_operations:
            return False

        return operation in self.allowed_operations

    def is_path_protected(
        self,
        path: str,
    ) -> bool:

        if not path.strip():
            raise ValueError(
                "Path cannot be empty."
            )

        normalized_path = path.lower()

        return any(
            protected.lower()
            in normalized_path
            for protected in self.protected_paths
        )

    def can_change(
        self,
        operation: str,
        path: str,
    ) -> bool:

        if not self.is_operation_allowed(
            operation
        ):
            return False

        if self.is_path_protected(path):
            return False

        return True

    def snapshot(self) -> Dict:
        """
        Return the current change policy.
        """

        return {
            "allowed_operations": sorted(
                self.allowed_operations
            ),
            "blocked_operations": sorted(
                self.blocked_operations
            ),
            "protected_paths": sorted(
                self.protected_paths
            ),
        }