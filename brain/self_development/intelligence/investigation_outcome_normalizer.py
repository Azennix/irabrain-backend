from brain.self_development.intelligence.investigation_outcome import (
    InvestigationOutcome,
)
from brain.self_development.intelligence.investigation_result_interpreter import (
    InvestigationInterpretation,
)


class InvestigationOutcomeNormalizer:
    """
    Converts the raw Foundation investigation interpretation
    into the stable Intelligence outcome contract.

    This layer only normalizes information.
    It does not authorize or execute any action.
    """

    def normalize(
        self,
        interpretation: InvestigationInterpretation | None,
    ) -> InvestigationOutcome:
        if interpretation is None:
            return InvestigationOutcome(
                status="not_required",
                actionable=False,
                reason="No investigation was required.",
                evidence={},
            )

        if not interpretation.success:
            return InvestigationOutcome(
                status="failed",
                actionable=False,
                reason=interpretation.reason,
                evidence=dict(interpretation.evidence),
            )

        return InvestigationOutcome(
            status="completed",
            actionable=interpretation.actionable,
            reason=interpretation.reason,
            evidence=dict(interpretation.evidence),
        )