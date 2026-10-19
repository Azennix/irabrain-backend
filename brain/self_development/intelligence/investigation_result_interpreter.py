from dataclasses import dataclass
from typing import Any

from brain.self_development.intelligence.foundation_result import (
    FoundationInvestigationResult,
)


@dataclass(frozen=True)
class InvestigationInterpretation:
    success: bool
    actionable: bool
    reason: str
    evidence: dict[str, Any]


class InvestigationResultInterpreter:
    """
    Interprets Foundation investigation results for the
    Self-Development Intelligence layer.

    This does not execute improvements or authorize actions.
    """

    def interpret(
        self,
        result: FoundationInvestigationResult,
    ) -> InvestigationInterpretation:

        if result is None:
            raise ValueError(
                "Foundation investigation result cannot be None."
            )

        if not result.success:
            return InvestigationInterpretation(
                success=False,
                actionable=False,
                reason=(
                    result.error
                    or "Foundation investigation failed."
                ),
                evidence=dict(result.evidence),
            )

        return InvestigationInterpretation(
            success=True,
            actionable=True,
            reason="Investigation completed successfully.",
            evidence=dict(result.evidence),
        )