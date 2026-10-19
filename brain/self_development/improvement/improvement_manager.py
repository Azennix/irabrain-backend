from datetime import datetime
from typing import List, Optional

from brain.self_development.domain.enums import ImprovementStatus
from brain.self_development.domain.models import (
    DevelopmentSignal,
    Improvement,
)


class ImprovementManager:
    """
    Manages improvement opportunities for IRABRAIN.

    Responsibilities:
    - receive development signals
    - create structured improvements
    - track improvement state
    - provide improvements for investigation/planning

    It does NOT:
    - modify source code
    - execute development
    - run tests
    - deploy changes
    - release versions
    """

    def __init__(self):
        self._improvements = {}
        self._counter = 0

    def create(
        self,
        signal: DevelopmentSignal,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: int = 0,
    ) -> Improvement:

        if signal is None:
            raise ValueError(
                "Development signal cannot be None."
            )

        self._counter += 1

        improvement_id = (
            f"IMP-{self._counter:04d}"
        )

        now = datetime.utcnow()

        improvement = Improvement(
            improvement_id=improvement_id,
            title=title or (
                f"Improve {signal.signal_type.value}"
            ),
            description=description or signal.description,
            status=ImprovementStatus.DETECTED,
            priority=priority,
            source_signals=[
                signal.signal_type.value
            ],
            created_at=now,
            updated_at=now,
        )

        self._improvements[
            improvement_id
        ] = improvement

        return improvement

    def get(
        self,
        improvement_id: str,
    ) -> Optional[Improvement]:

        return self._improvements.get(
            improvement_id
        )

    def list_improvements(
        self,
    ) -> List[Improvement]:

        return list(
            self._improvements.values()
        )

    def update_status(
        self,
        improvement_id: str,
        status: ImprovementStatus,
    ) -> Improvement:

        improvement = self.get(
            improvement_id
        )

        if improvement is None:
            raise ValueError(
                f"Unknown improvement: "
                f"{improvement_id}"
            )

        if not isinstance(
            status,
            ImprovementStatus,
        ):
            raise ValueError(
                "status must be an ImprovementStatus."
            )

        improvement.status = status
        improvement.updated_at = datetime.utcnow()

        return improvement