from typing import List

from brain.self_development.domain.models import (
    DevelopmentSignal,
    Improvement,
)
from brain.self_development.observation.signal_detector import (
    DetectedPattern,
    SignalDetector,
)
from brain.self_development.improvement.improvement_manager import (
    ImprovementManager,
)


class ObservationCoordinator:
    """
    Coordinates the observation-to-improvement boundary.

    Responsibilities:
    - receive development signals
    - pass signals to SignalDetector
    - convert actionable detected patterns into improvements

    It does NOT:
    - modify source code
    - execute development
    - start self-development cycles
    - authorize changes
    - deploy releases
    """

    def __init__(
        self,
        signal_detector: SignalDetector,
        improvement_manager: ImprovementManager,
    ):
        if signal_detector is None:
            raise ValueError(
                "Signal detector cannot be None."
            )

        if improvement_manager is None:
            raise ValueError(
                "Improvement manager cannot be None."
            )

        self.signal_detector = signal_detector
        self.improvement_manager = improvement_manager

    def process(
        self,
        signals: List[DevelopmentSignal],
    ) -> List[Improvement]:
        """
        Detect meaningful patterns and create improvements
        from the signals associated with those patterns.
        """

        if not signals:
            return []

        patterns: List[DetectedPattern] = (
            self.signal_detector.detect(signals)
        )

        improvements: List[Improvement] = []


        for pattern in patterns:
            if not pattern.signals:
                continue

            representative_signal = pattern.signals[0]


            improvement = self.improvement_manager.create(
                signal=representative_signal,
                title=pattern.name,
                description=pattern.description,
                priority=self._priority_from_severity(
                    pattern.severity
                    ),
                )

            improvements.append(improvement)

        return improvements

    @staticmethod
    def _priority_from_severity(
        severity,
    ) -> int:
        """
        Convert signal severity into an improvement priority.
        """

        priority = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }

        return priority.get(
            severity.value,
            0,
        )