from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass(frozen=True)
class PipelineEvidence:
    """
    Structured evidence collected during one
    self-development cycle.
    """

    cycle_id: str
    evidence: Dict[str, Any] = field(
        default_factory=dict
    )
    collected_at: datetime = field(
        default_factory=datetime.utcnow
    )


class PipelineEvidenceCollector:
    """
    Collects stage results for a self-development cycle.

    Responsibilities:
    - record results from pipeline stages
    - keep evidence associated with a cycle
    - provide a complete evidence snapshot

    It does NOT:
    - make release decisions
    - modify source code
    - execute development
    - deploy candidates
    """

    def __init__(self):
        self._evidence: Dict[
            str,
            Dict[str, Any],
        ] = {}

    def record(
        self,
        cycle_id: str,
        stage: str,
        result: Any,
    ) -> None:

        if not cycle_id.strip():
            raise ValueError(
                "Cycle ID cannot be empty."
            )

        if not stage.strip():
            raise ValueError(
                "Stage cannot be empty."
            )

        self._evidence.setdefault(
            cycle_id,
            {},
        )[stage] = result

    def get(
        self,
        cycle_id: str,
    ) -> PipelineEvidence:

        if not cycle_id.strip():
            raise ValueError(
                "Cycle ID cannot be empty."
            )

        return PipelineEvidence(
            cycle_id=cycle_id,
            evidence=dict(
                self._evidence.get(
                    cycle_id,
                    {},
                )
            ),
        )

    def has(
        self,
        cycle_id: str,
        stage: str,
    ) -> bool:

        if not cycle_id.strip():
            raise ValueError(
                "Cycle ID cannot be empty."
            )

        if not stage.strip():
            raise ValueError(
                "Stage cannot be empty."
            )

        return stage in self._evidence.get(
            cycle_id,
            {},
        )

    def clear(
        self,
        cycle_id: str,
    ) -> None:

        if not cycle_id.strip():
            raise ValueError(
                "Cycle ID cannot be empty."
            )

        self._evidence.pop(
            cycle_id,
            None,
        )