from dataclasses import dataclass

from brain.reasoning.strategies import ReasoningStrategy


@dataclass(frozen=True, slots=True)
class StrategyContract:

    strategy: ReasoningStrategy

    requires_alternatives: bool = False
    requires_risks: bool = False
    requires_assumptions: bool = False

    def validate(self, result) -> list[str]:

        violations = []

        if self.requires_alternatives:
            if not result.alternatives:
                violations.append(
                    "alternatives_required"
                )

        if self.requires_risks:
            if not result.risks:
                violations.append(
                    "risks_required"
                )

        if self.requires_assumptions:
            if not result.assumptions:
                violations.append(
                    "assumptions_required"
                )

        return violations