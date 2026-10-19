from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class PipelineStage(str, Enum):
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


@dataclass
class PipelineState:
    """
    Represents the current state of one
    self-development cycle.
    """

    cycle_id: str
    stage: PipelineStage = PipelineStage.OBSERVATION

    improvement_id: Optional[str] = None
    experiment_id: Optional[str] = None
    candidate_id: Optional[str] = None
    staging_id: Optional[str] = None
    canary_id: Optional[str] = None
    release_id: Optional[str] = None

    metadata: Dict = field(
        default_factory=dict
    )

    started_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    def transition(
        self,
        stage: PipelineStage,
    ) -> None:
        """
        Move the pipeline to a new stage.
        """

        self.stage = stage
        self.updated_at = datetime.utcnow()

    def set_reference(
        self,
        name: str,
        value: str,
    ) -> None:
        """
        Store an identifier produced by a
        pipeline component.
        """

        if not name.strip():
            raise ValueError(
                "Reference name cannot be empty."
            )

        if not value.strip():
            raise ValueError(
                "Reference value cannot be empty."
            )

        if not hasattr(self, name):
            raise ValueError(
                f"Unknown pipeline reference: {name}"
            )

        setattr(self, name, value)
        self.updated_at = datetime.utcnow()

    def add_metadata(
        self,
        key: str,
        value,
    ) -> None:
        """
        Store additional pipeline information.
        """

        if not key.strip():
            raise ValueError(
                "Metadata key cannot be empty."
            )

        self.metadata[key] = value
        self.updated_at = datetime.utcnow()

    def snapshot(self) -> Dict:
        """
        Return the complete current pipeline state.
        """

        return {
            "cycle_id": self.cycle_id,
            "stage": self.stage.value,
            "improvement_id": self.improvement_id,
            "experiment_id": self.experiment_id,
            "candidate_id": self.candidate_id,
            "staging_id": self.staging_id,
            "canary_id": self.canary_id,
            "release_id": self.release_id,
            "metadata": dict(self.metadata),
            "started_at": self.started_at,
            "updated_at": self.updated_at,
        }