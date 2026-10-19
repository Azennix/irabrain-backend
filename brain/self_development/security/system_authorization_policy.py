from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class SystemAuthorizationDecision:
    """
    Authorization result for IRABRAIN's autonomous
    self-development system.

    This authorization domain is completely separate
    from Human Authorization.
    """

    allowed: bool
    action: str
    reason: str


class SystemAuthorizationPolicy:
    """
    Controls whether IRABRAIN's autonomous
    self-development system is authorized to
    perform a system-level self-development action.

    Responsibilities:
    - authorize autonomous self-development actions
    - fail closed for unknown or invalid actions
    - provide a stable authorization boundary

    Does NOT:
    - authenticate human users
    - execute actions
    - control capabilities
    - perform code changes
    - deploy or release
    """

    ALLOWED_ACTIONS = frozenset(
        {
            "observation",
            "investigation",
            "planning",
            "development",
            "testing",
            "evaluation",
            "staging",
            "canary",
            "rollback",
            "monitoring",
        }
    )

    def authorize(
        self,
        action: str,
    ) -> SystemAuthorizationDecision:

        if not isinstance(action, str):
            raise ValueError(
                "System authorization action must be a string."
            )

        action = action.strip()

        if not action:
            raise ValueError(
                "System authorization action cannot be empty."
            )

        if action not in self.ALLOWED_ACTIONS:
            return SystemAuthorizationDecision(
                allowed=False,
                action=action,
                reason=(
                    "Action is not authorized for "
                    "autonomous self-development."
                ),
            )

        return SystemAuthorizationDecision(
            allowed=True,
            action=action,
            reason=(
                "Action is authorized for "
                "autonomous self-development."
            ),
        )

    def is_authorized(
        self,
        action: str,
    ) -> bool:

        return self.authorize(action).allowed

    def snapshot(self) -> Dict[str, object]:
        return {
            "authorization_domain": (
                "system_autonomous_self_development"
            ),
            "allowed_actions": sorted(
                self.ALLOWED_ACTIONS
            ),
        }