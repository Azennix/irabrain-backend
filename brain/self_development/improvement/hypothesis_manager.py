from datetime import datetime
from typing import List, Optional

from brain.self_development.domain.enums import HypothesisStatus
from brain.self_development.domain.models import (
    Hypothesis,
    Improvement,
)


class HypothesisManager:
    """
    Manages hypotheses for improvements.

    Responsibilities:
    - create hypotheses
    - validate hypothesis input
    - retrieve hypotheses
    - associate hypotheses with improvements
    - track hypothesis lifecycle

    It does NOT:
    - modify source code
    - execute development
    - run tests
    - deploy changes
    - decide final root cause
    """

    def __init__(self):
        self._hypotheses = {}
        self._counter = 0

    def create(
        self,
        improvement: Improvement,
        statement: str,
        confidence: float = 0.0,
    ) -> Hypothesis:

        if improvement is None:
            raise ValueError(
                "Improvement cannot be None."
            )

        if not statement.strip():
            raise ValueError(
                "Hypothesis statement cannot be empty."
            )

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "Hypothesis confidence must be between 0.0 and 1.0."
            )

        self._counter += 1

        hypothesis_id = (
            f"HYP-{self._counter:04d}"
        )

        hypothesis = Hypothesis(
            hypothesis_id=hypothesis_id,
            improvement_id=improvement.improvement_id,
            statement=statement,
            status=HypothesisStatus.PROPOSED,
            confidence=confidence,
        )

        self._hypotheses[
            hypothesis_id
        ] = hypothesis

        return hypothesis

    def get(
        self,
        hypothesis_id: str,
    ) -> Optional[Hypothesis]:

        return self._hypotheses.get(
            hypothesis_id
        )

    def list_for_improvement(
        self,
        improvement_id: str,
    ) -> List[Hypothesis]:

        return [
            hypothesis
            for hypothesis in self._hypotheses.values()
            if hypothesis.improvement_id == improvement_id
        ]

    def list_all(
        self,
    ) -> List[Hypothesis]:

        return list(
            self._hypotheses.values()
        )

    def update_status(
        self,
        hypothesis_id: str,
        status: HypothesisStatus,
    ) -> Hypothesis:

        hypothesis = self.get(
            hypothesis_id
        )

        if hypothesis is None:
            raise ValueError(
                f"Unknown hypothesis: "
                f"{hypothesis_id}"
            )

        if not isinstance(
            status,
            HypothesisStatus,
        ):
            raise ValueError(
                "status must be a HypothesisStatus."
            )

        hypothesis.status = status

        return hypothesis