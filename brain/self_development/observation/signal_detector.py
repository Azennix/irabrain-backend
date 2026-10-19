from dataclasses import dataclass
from typing import List

from ..domain.enums import SignalSeverity
from ..domain.models import DevelopmentSignal


@dataclass(frozen=True)
class DetectedPattern:
    """
    Represents a meaningful pattern detected from
    one or more development signals.
    """

    name: str
    description: str
    severity: SignalSeverity
    signals: List[DevelopmentSignal]


class SignalDetector:
    """
    Detects meaningful development patterns from
    collected system signals.

    Responsibilities:
    - inspect collected signals
    - identify meaningful patterns
    - determine pattern severity
    - return structured detection results

    It does NOT:
    - create improvements
    - investigate root causes
    - modify code
    - execute development
    - release changes
    """

    def detect(
        self,
        signals: List[DevelopmentSignal],
    ) -> List[DetectedPattern]:

        if not signals:
            return []

        patterns: List[DetectedPattern] = []

        # -------------------------------------------------
        # GROUP SIGNALS BY TYPE
        # -------------------------------------------------

        grouped = {}

        for signal in signals:
            grouped.setdefault(
                signal.signal_type,
                []
            ).append(signal)

        # -------------------------------------------------
        # DETECT REPEATED SIGNALS
        # -------------------------------------------------

        for signal_type, matching_signals in grouped.items():

            if len(matching_signals) < 2:
                continue

            severity = self._highest_severity(
                matching_signals
            )

            patterns.append(
                DetectedPattern(
                    name=f"repeated_{signal_type.value}",
                    description=(
                        f"Repeated {signal_type.value} "
                        "signals were detected."
                    ),
                    severity=severity,
                    signals=matching_signals,
                )
            )

        # -------------------------------------------------
        # DETECT HIGH / CRITICAL SIGNALS
        # -------------------------------------------------

        for signal in signals:

            if signal.severity in (
                SignalSeverity.HIGH,
                SignalSeverity.CRITICAL,
            ):

                patterns.append(
                    DetectedPattern(
                        name=f"significant_{signal.signal_type.value}",
                        description=(
                            f"A {signal.severity.value} "
                            f"{signal.signal_type.value} signal "
                            "requires attention."
                        ),
                        severity=signal.severity,
                        signals=[signal],
                    )
                )

        return patterns

    # =====================================================
    # SEVERITY
    # =====================================================

    @staticmethod
    def _highest_severity(
        signals: List[DevelopmentSignal],
    ) -> SignalSeverity:

        priority = {
            SignalSeverity.LOW: 1,
            SignalSeverity.MEDIUM: 2,
            SignalSeverity.HIGH: 3,
            SignalSeverity.CRITICAL: 4,
        }

        return max(
            signals,
            key=lambda signal: priority[
                signal.severity
            ],
        ).severity