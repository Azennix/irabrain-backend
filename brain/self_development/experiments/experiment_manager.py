from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class ExperimentStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Experiment:
    """
    Represents a controlled self-development experiment.
    """

    experiment_id: str
    improvement_id: str
    objective: str
    status: ExperimentStatus = ExperimentStatus.CREATED
    result: Optional[Dict] = None
    created_at: datetime = field(
        default_factory=datetime.utcnow
    )
    completed_at: Optional[datetime] = None


class ExperimentManager:
    """
    Manages controlled development experiments.

    Responsibilities:
    - create experiments
    - start experiments
    - record experiment results
    - complete or fail experiments
    - provide experiment state

    It does NOT:
    - modify production code
    - deploy releases
    - bypass validation
    - make autonomous production decisions
    """

    def __init__(self):
        self._experiments: Dict[
            str, Experiment
        ] = {}
        self._counter = 0

    def create(
        self,
        improvement_id: str,
        objective: str,
    ) -> Experiment:

        if not improvement_id.strip():
            raise ValueError(
                "Improvement ID cannot be empty."
            )

        if not objective.strip():
            raise ValueError(
                "Experiment objective cannot be empty."
            )

        self._counter += 1

        experiment_id = (
            f"EXP-{self._counter:04d}"
        )

        experiment = Experiment(
            experiment_id=experiment_id,
            improvement_id=improvement_id,
            objective=objective,
        )

        self._experiments[
            experiment_id
        ] = experiment

        return experiment

    def start(
        self,
        experiment_id: str,
    ) -> Experiment:

        experiment = self._get(
            experiment_id
        )

        if experiment.status != (
            ExperimentStatus.CREATED
        ):
            raise ValueError(
                "Only a created experiment can be started."
            )

        experiment.status = (
            ExperimentStatus.RUNNING
        )

        return experiment

    def complete(
        self,
        experiment_id: str,
        result: Dict,
    ) -> Experiment:

        experiment = self._get(
            experiment_id
        )

        if experiment.status != (
            ExperimentStatus.RUNNING
        ):
            raise ValueError(
                "Only a running experiment can be completed."
            )

        experiment.result = dict(result)
        experiment.status = (
            ExperimentStatus.COMPLETED
        )
        experiment.completed_at = datetime.utcnow()

        return experiment

    def fail(
        self,
        experiment_id: str,
        result: Optional[Dict] = None,
    ) -> Experiment:

        experiment = self._get(
            experiment_id
        )

        if experiment.status != (
            ExperimentStatus.RUNNING
        ):
            raise ValueError(
                "Only a running experiment can fail."
            )

        experiment.result = (
            dict(result)
            if result is not None
            else None
        )

        experiment.status = (
            ExperimentStatus.FAILED
        )
        experiment.completed_at = datetime.utcnow()

        return experiment

    def get(
        self,
        experiment_id: str,
    ) -> Optional[Experiment]:

        return self._experiments.get(
            experiment_id
        )

    def _get(
        self,
        experiment_id: str,
    ) -> Experiment:

        experiment = self.get(
            experiment_id
        )

        if experiment is None:
            raise ValueError(
                f"Experiment not found: {experiment_id}"
            )

        return experiment