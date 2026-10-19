from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .enums import (
    DevelopmentStatus,
    EvaluationStatus,
    HypothesisStatus,
    ImprovementStatus,
    PipelineStage,
    ReleaseStatus,
    SignalSeverity,
    SignalType,
    ValidationStatus,
)


@dataclass(frozen=True)
class DevelopmentSignal:
    """
    A structured observation produced by the
    self-development observation layer.
    """

    signal_type: SignalType
    severity: SignalSeverity
    source: str
    description: str

    evidence: Dict[str, Any] = field(
        default_factory=dict
    )

    detected_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class Improvement:
    """
    Represents a potential improvement opportunity
    identified by IRABRAIN.
    """

    improvement_id: str
    title: str
    description: str

    status: ImprovementStatus = (
        ImprovementStatus.DETECTED
    )

    priority: int = 0

    source_signals: List[str] = field(
        default_factory=list
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class Hypothesis:
    """
    A testable explanation for why an improvement
    may be necessary.
    """

    hypothesis_id: str
    improvement_id: str

    statement: str

    status: HypothesisStatus = (
        HypothesisStatus.PROPOSED
    )

    confidence: float = 0.0

    evidence: List[Dict[str, Any]] = field(
        default_factory=list
    )


@dataclass
class Evidence:
    """
    Evidence collected while investigating an
    improvement opportunity.
    """

    evidence_id: str
    source: str
    description: str

    data: Dict[str, Any] = field(
        default_factory=dict
    )

    collected_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class DevelopmentPlan:
    """
    Structured plan describing how an improvement
    should be developed.
    """

    plan_id: str
    improvement_id: str

    objective: str

    steps: List[str] = field(
        default_factory=list
    )

    constraints: List[str] = field(
        default_factory=list
    )

    expected_outcome: str = ""


@dataclass
class DevelopmentResult:
    """
    Result produced by the development phase.
    """

    development_id: str
    improvement_id: str

    status: DevelopmentStatus

    workspace: Optional[str] = None

    changed_files: List[str] = field(
        default_factory=list
    )

    details: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ValidationResult:
    """
    Result of technical validation of a candidate
    change.
    """

    validation_id: str
    improvement_id: str

    status: ValidationStatus

    tests_passed: int = 0
    tests_failed: int = 0

    build_passed: Optional[bool] = None
    lint_passed: Optional[bool] = None

    details: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class EvaluationResult:
    """
    Compares a candidate improvement against
    an existing baseline.
    """

    evaluation_id: str
    improvement_id: str

    status: EvaluationStatus

    baseline_score: Optional[float] = None
    candidate_score: Optional[float] = None

    confidence: float = 0.0

    details: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ReleaseDecision:
    """
    Decision produced by the release policy layer.
    """

    improvement_id: str

    approved: bool

    status: ReleaseStatus

    reason: str

    conditions: List[str] = field(
        default_factory=list
    )


@dataclass
class PipelineState:
    """
    Current state of one self-development cycle.
    """

    cycle_id: str

    stage: PipelineStage = PipelineStage.OBSERVATION

    improvement_id: Optional[str] = None

    signal: Optional[DevelopmentSignal] = None

    improvement: Optional[Improvement] = None

    hypothesis: Optional[Hypothesis] = None

    evidence: List[Evidence] = field(
        default_factory=list
    )

    plan: Optional[DevelopmentPlan] = None

    development: Optional[DevelopmentResult] = None

    validation: Optional[ValidationResult] = None

    evaluation: Optional[EvaluationResult] = None

    release: Optional[ReleaseDecision] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )