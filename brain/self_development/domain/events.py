from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from .enums import PipelineStage


@dataclass(frozen=True)
class SelfDevelopmentEvent:
    """
    Base event emitted during a self-development cycle.

    Events describe what happened.
    They do not execute business logic themselves.
    """

    event_id: str
    event_type: str
    cycle_id: str

    stage: PipelineStage

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )

    payload: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SignalDetectedEvent(SelfDevelopmentEvent):
    """
    Emitted when the observation layer detects
    a meaningful development signal.
    """

    signal_id: str = ""


@dataclass(frozen=True)
class ImprovementCreatedEvent(SelfDevelopmentEvent):
    """
    Emitted when a development opportunity is
    converted into an improvement item.
    """

    improvement_id: str = ""


@dataclass(frozen=True)
class InvestigationCompletedEvent(SelfDevelopmentEvent):
    """
    Emitted after investigation produces evidence
    and a root-cause understanding.
    """

    improvement_id: str = ""


@dataclass(frozen=True)
class PlanCreatedEvent(SelfDevelopmentEvent):
    """
    Emitted when an improvement plan is prepared.
    """

    improvement_id: str = ""
    plan_id: str = ""


@dataclass(frozen=True)
class DevelopmentCompletedEvent(SelfDevelopmentEvent):
    """
    Emitted when development produces a candidate
    change.
    """

    improvement_id: str = ""
    development_id: str = ""


@dataclass(frozen=True)
class ValidationCompletedEvent(SelfDevelopmentEvent):
    """
    Emitted after technical validation of a
    candidate change.
    """

    improvement_id: str = ""
    validation_id: str = ""


@dataclass(frozen=True)
class EvaluationCompletedEvent(SelfDevelopmentEvent):
    """
    Emitted after comparing the candidate against
    the existing baseline.
    """

    improvement_id: str = ""
    evaluation_id: str = ""


@dataclass(frozen=True)
class ReleaseDecisionEvent(SelfDevelopmentEvent):
    """
    Emitted when the release-policy layer makes
    a release decision.
    """

    improvement_id: str = ""
    approved: bool = False


@dataclass(frozen=True)
class ReleaseCompletedEvent(SelfDevelopmentEvent):
    """
    Emitted after a controlled release operation.
    """

    improvement_id: str = ""
    release_id: Optional[str] = None


@dataclass(frozen=True)
class RollbackEvent(SelfDevelopmentEvent):
    """
    Emitted when a released candidate must be
    rolled back.
    """

    improvement_id: str = ""
    reason: str = ""