from enum import Enum


class SignalType(str, Enum):
    """
    Types of signals that can indicate a possible
    improvement opportunity inside IRABRAIN.
    """

    ERROR = "error"
    FAILURE = "failure"
    PERFORMANCE = "performance"
    REGRESSION = "regression"
    TEST_FAILURE = "test_failure"
    CAPABILITY_GAP = "capability_gap"
    USER_FEEDBACK = "user_feedback"
    SYSTEM_HEALTH = "system_health"


class SignalSeverity(str, Enum):
    """
    Severity of an observed signal.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImprovementStatus(str, Enum):
    """
    Lifecycle state of an improvement.
    """

    DETECTED = "detected"
    QUEUED = "queued"
    INVESTIGATING = "investigating"
    PLANNED = "planned"
    DEVELOPING = "developing"
    VALIDATING = "validating"
    EVALUATING = "evaluating"
    APPROVED = "approved"
    RELEASED = "released"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"
    COMPLETED = "completed"


class HypothesisStatus(str, Enum):
    """
    Lifecycle state of an improvement hypothesis.
    """

    PROPOSED = "proposed"
    TESTING = "testing"
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"


class DevelopmentStatus(str, Enum):
    """
    State of a development operation.
    """

    NOT_STARTED = "not_started"
    PREPARING = "preparing"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ValidationStatus(str, Enum):
    """
    Result of validating a candidate change.
    """

    NOT_RUN = "not_run"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


class EvaluationStatus(str, Enum):
    """
    Result of evaluating an improvement candidate
    against the existing baseline.
    """

    NOT_EVALUATED = "not_evaluated"
    IMPROVED = "improved"
    UNCHANGED = "unchanged"
    DEGRADED = "degraded"
    INCONCLUSIVE = "inconclusive"


class ReleaseStatus(str, Enum):
    """
    State of a controlled release.
    """

    NOT_READY = "not_ready"
    STAGING = "staging"
    CANARY = "canary"
    RELEASED = "released"
    ROLLED_BACK = "rolled_back"


class PipelineStage(str, Enum):
    """
    Major stages of the self-development pipeline.
    """

    OBSERVATION = "observation"
    IMPROVEMENT = "improvement"
    INVESTIGATION = "investigation"
    PLANNING = "planning"
    DEVELOPMENT = "development"
    VALIDATION = "validation"
    EVALUATION = "evaluation"
    EXPERIMENT = "experiment"
    STAGING = "staging"
    CANARY = "canary"
    RELEASE = "release"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    FAILED = "failed"