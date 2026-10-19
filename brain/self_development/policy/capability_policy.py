from dataclasses import dataclass, field
from typing import Dict


@dataclass
class CapabilityPolicy:
    """
    Defines which self-development capabilities
    are currently allowed.
    """

    capabilities: Dict[str, bool] = field(
        default_factory=lambda: {
            "observation": True,
            "investigation": True,
            "planning": True,
            "development": True,
            "testing": True,
            "evaluation": True,
            "experimentation": True,
            "staging": True,
            "canary": True,
            "rollback": True,
            "monitoring": True,
            "production_release": False,
        }
    )

    def is_allowed(
        self,
        capability: str,
    ) -> bool:
        """
        Check whether a capability is allowed.
        """

        if not capability.strip():
            raise ValueError(
                "Capability name cannot be empty."
            )

        return self.capabilities.get(
            capability,
            False,
        )

    def enable(
        self,
        capability: str,
    ) -> None:

        if not capability.strip():
            raise ValueError(
                "Capability name cannot be empty."
            )

        self.capabilities[capability] = True

    def disable(
        self,
        capability: str,
    ) -> None:

        if not capability.strip():
            raise ValueError(
                "Capability name cannot be empty."
            )

        self.capabilities[capability] = False

    def snapshot(self) -> Dict[str, bool]:
        """
        Return the current capability policy.
        """

        return dict(self.capabilities)