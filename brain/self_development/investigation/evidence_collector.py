from typing import Any, Dict, List

from brain.self_development.domain.models import Evidence


class EvidenceCollector:
    """
    Collects and organizes evidence related to an
    improvement investigation.

    Responsibilities:
    - receive evidence from different sources
    - keep evidence structured
    - return collected evidence

    It does NOT:
    - decide the root cause
    - modify source code
    - execute development
    - run tests
    - deploy changes
    """

    def __init__(self):
        self._evidence: Dict[str, List[Evidence]] = {}
        self._counter = 0

    def collect(
        self,
        improvement_id: str,
        source: str,
        description: str,
        data: Any,
    ) -> Evidence:

        if not improvement_id.strip():
            raise ValueError(
                "Improvement ID cannot be empty."
            )

        if not source.strip():
            raise ValueError(
                "Evidence source cannot be empty."
            )

        if not description.strip():
            raise ValueError(
                "Evidence description cannot be empty."
            )

        self._counter += 1

        evidence_id = (
            f"EVD-{self._counter:04d}"
        )

        evidence = Evidence(
            evidence_id=evidence_id,
            source=source,
            description=description,
            data=data if isinstance(data, dict) else {
                "value": data
            },
        )

        self._evidence.setdefault(
            improvement_id,
            []
        ).append(evidence)

        return evidence

    def get_for_improvement(
        self,
        improvement_id: str,
    ) -> List[Evidence]:

        return list(
            self._evidence.get(
                improvement_id,
                []
            )
        )

    def count(
        self,
        improvement_id: str,
    ) -> int:

        return len(
            self._evidence.get(
                improvement_id,
                []
            )
        )