from dataclasses import dataclass
from typing import Callable, Any
from brain.reasoning.evidence import Evidence, EvidenceSource

from brain.reasoning.strategies import ReasoningStrategy


@dataclass(frozen=True, slots=True)
class ReasoningRule:
    name: str
    check: Callable[[Any], bool]


class ReasoningRules:

    def __init__(self):
        self._rules: list[ReasoningRule] = [
            ReasoningRule(
                name="valid_conclusion",
                check=self._valid_conclusion
            ),
            ReasoningRule(
                name="valid_confidence",
                check=self._valid_confidence
            ),
            ReasoningRule(
                name="evidence_is_list",
                check=self._evidence_is_list
            ),
            ReasoningRule(
                name="alternatives_is_list",
                check=self._alternatives_is_list
            ),
            ReasoningRule(
                name="risks_is_list",
                check=self._risks_is_list
            ),
            ReasoningRule(
                name="assumptions_is_list",
                check=self._assumptions_is_list
            ),
            ReasoningRule(
               name="valid_evidence_items",
               check=self._valid_evidence_items
),
            ReasoningRule(
               name="valid_evidence_confidence",
               check=self._valid_evidence_confidence
),
            ReasoningRule(
              name="valid_evidence_sources",
              check=self._valid_evidence_sources


),
            ReasoningRule(
              name="valid_strategy",
              check=self._valid_strategy
),


        ]

    def validate(
        self,
        result: Any
    ) -> list[str]:

        violations = []

        for rule in self._rules:

            try:
                passed = rule.check(result)

            except Exception:
                passed = False

            if not passed:
                violations.append(
                    rule.name
                )

        return violations

    # ==========================================
    # RULES
    # ==========================================

    @staticmethod
    def _valid_conclusion(
        result: Any
    ) -> bool:

        return (
            isinstance(result.conclusion, str)
            and bool(result.conclusion.strip())
        )

    @staticmethod
    def _valid_confidence(
        result: Any
    ) -> bool:

        return (
            isinstance(result.confidence, (int, float))
            and 0.0 <= result.confidence <= 1.0
        )

    @staticmethod
    def _evidence_is_list(
        result: Any
    ) -> bool:

        return isinstance(result.evidence, list)

    @staticmethod
    def _alternatives_is_list(
        result: Any
    ) -> bool:

        return isinstance(result.alternatives, list)

    @staticmethod
    def _risks_is_list(
        result: Any
    ) -> bool:

        return isinstance(result.risks, list)

    @staticmethod
    def _assumptions_is_list(
        result: Any
    ) -> bool:

        return isinstance(result.assumptions, list)

    @staticmethod
    def _valid_evidence_items(
    result: Any
) -> bool:

        return all(
        isinstance(item, Evidence)
        and isinstance(item.content, str)
        and bool(item.content.strip())
        for item in result.evidence
    )

    @staticmethod
    def _valid_evidence_confidence(
    result: Any
) -> bool:

        return all(
        isinstance(item.confidence, (int, float))
        and 0.0 <= item.confidence <= 1.0
        for item in result.evidence
    )

    @staticmethod
    def _valid_evidence_sources(
    result: Any
) -> bool:

        return all(
        isinstance(
            item.source,
            EvidenceSource
        )
        for item in result.evidence
    )


    @staticmethod
    def _valid_strategy(
    result: Any
) -> bool:

     return isinstance(
        result.strategy,
        ReasoningStrategy
    )