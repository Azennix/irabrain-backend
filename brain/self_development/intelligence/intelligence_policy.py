from dataclasses import dataclass


@dataclass(frozen=True)
class IntelligencePolicyDecision:
    allowed: bool
    action: str
    reason: str


class SelfDevelopmentIntelligencePolicy:
    """
    Defines what the Intelligence layer itself is allowed to do.

    Intelligence can observe, investigate, and interpret.
    It cannot execute self-development actions.
    """

    ALLOWED_ACTIONS = frozenset(
        {
            "observation",
            "investigation",
            "interpretation",
        }
    )

    def authorize(
        self,
        action: str,
    ) -> IntelligencePolicyDecision:

        if not isinstance(action, str):
            raise ValueError(
                "Intelligence action must be a string."
            )

        normalized_action = action.strip().lower()

        if not normalized_action:
            raise ValueError(
                "Intelligence action cannot be empty."
            )

        if normalized_action in self.ALLOWED_ACTIONS:
            return IntelligencePolicyDecision(
                allowed=True,
                action=normalized_action,
                reason="Action is authorized for intelligence.",
            )

        return IntelligencePolicyDecision(
            allowed=False,
            action=normalized_action,
            reason=(
                "Action is not authorized for "
                "self-development intelligence."
            ),
        )

    def is_authorized(self, action: str) -> bool:
        return self.authorize(action).allowed