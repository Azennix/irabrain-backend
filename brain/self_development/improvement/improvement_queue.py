from datetime import datetime
from typing import List, Optional

from brain.self_development.domain.enums import ImprovementStatus
from brain.self_development.domain.models import Improvement


class ImprovementQueue:
    """
    Manages the ordered queue of improvements.

    Responsibilities:
    - add improvements
    - maintain priority order
    - retrieve the next eligible improvement
    - remove completed/rejected improvements

    It does NOT:
    - investigate problems
    - modify source code
    - execute development
    - run tests
    - deploy releases
    """

    def __init__(self):
        self._queue: List[Improvement] = []

    def add(
        self,
        improvement: Improvement,
    ) -> None:

        if improvement is None:
            raise ValueError(
                "Improvement cannot be None."
            )

        if improvement not in self._queue:
            self._queue.append(improvement)

        self._sort()

    def _sort(self) -> None:
        """
        Sort by explicit improvement priority,
        then creation time.
        """

        self._queue.sort(
            key=lambda improvement: (
                -improvement.priority,
                improvement.created_at,
            )
        )

    def next(
        self,
    ) -> Optional[Improvement]:
        """
        Return the highest-priority improvement
        waiting for investigation.
        """

        eligible_statuses = {
            ImprovementStatus.DETECTED,
            ImprovementStatus.QUEUED,
        }

        for improvement in self._queue:

            if improvement.status in eligible_statuses:
                return improvement

        return None

    def remove(
        self,
        improvement_id: str,
    ) -> bool:

        for improvement in self._queue:

            if (
                improvement.improvement_id
                == improvement_id
            ):
                self._queue.remove(improvement)
                return True

        return False

    def list(
        self,
    ) -> List[Improvement]:

        return list(self._queue)

    def size(self) -> int:
        return len(self._queue)