from typing import Any, Dict, Optional

from ..domain.enums import SignalSeverity, SignalType
from ..domain.models import DevelopmentSignal


class SignalCollector:
    """
    Collects development-related signals from IRABRAIN.

    Responsibilities:
    - receive observable system signals
    - normalize signal information
    - convert observations into DevelopmentSignal objects

    It does NOT:
    - decide whether an improvement should be created
    - investigate root causes
    - modify code
    - execute development
    - release changes
    """

    def collect(
        self,
        signal_type: SignalType,
        severity: SignalSeverity,
        source: str,
        description: str,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> DevelopmentSignal:
        """
        Convert an observed system event into a
        structured development signal.
        """

        if not source.strip():
            raise ValueError(
                "Signal source cannot be empty."
            )

        if not description.strip():
            raise ValueError(
                "Signal description cannot be empty."
            )

        return DevelopmentSignal(
            signal_type=signal_type,
            severity=severity,
            source=source,
            description=description,
            evidence=evidence or {},
        )