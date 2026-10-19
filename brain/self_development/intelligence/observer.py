from dataclasses import dataclass
from typing import Any

from brain.self_development.integration.core_execution_signal import (
    CoreExecutionSignal,
)


@dataclass(frozen=True)
class SelfDevelopmentObservation:
    """
    Interpretation of a Core execution signal.

    This is an observation only.
    It does not authorize or execute any change.
    """

    signal_id: str
    operation: str
    success: bool
    requires_investigation: bool
    reason: str
    evidence: dict[str, Any]


class SelfDevelopmentObserver:

    def observe(
        self,
        signal: CoreExecutionSignal,
    ) -> SelfDevelopmentObservation:

        if signal is None:
            raise ValueError(
                "Core execution signal cannot be None."
            )

        if not signal.success:

            return SelfDevelopmentObservation(
                signal_id=signal.signal_id,
                operation=signal.operation,
                success=False,
                requires_investigation=True,
                reason="Core execution failed.",
                evidence={
                    "error": signal.error,
                    "execution_time": signal.execution_time,
                },
            )

        return SelfDevelopmentObservation(
            signal_id=signal.signal_id,
            operation=signal.operation,
            success=True,
            requires_investigation=False,
            reason="Core execution completed successfully.",
            evidence={
                "execution_time": signal.execution_time,
            },
        )