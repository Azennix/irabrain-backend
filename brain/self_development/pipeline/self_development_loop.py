from dataclasses import dataclass
from typing import Optional

from brain.self_development.domain.enums import PipelineStage
from brain.self_development.domain.models import PipelineState


@dataclass(frozen=True)
class PipelineResult:
    """
    Result returned by a self-development pipeline cycle.
    """

    success: bool
    state: PipelineState
    message: str


class SelfDevelopmentLoop:
    """
    Central coordinator for the IRABRAIN
    self-development lifecycle.

    This component coordinates the pipeline state.

    It does NOT:
    - contain subsystem logic
    - generate arbitrary code
    - bypass policies
    - directly deploy production changes
    """

    def __init__(self):
        self._cycle_counter = 0
        self._current_state: Optional[PipelineState] = None

    def start_cycle(self) -> PipelineState:
        """
        Start a new self-development cycle.
        """

        self._cycle_counter += 1

        cycle_id = f"CYCLE-{self._cycle_counter:04d}"

        self._current_state = PipelineState(
            cycle_id=cycle_id,
            stage=PipelineStage.OBSERVATION,
        )

        return self._current_state

    def current_state(self) -> Optional[PipelineState]:
        """
        Return the active pipeline state.
        """

        return self._current_state

    def transition(
        self,
        stage: PipelineStage,
    ) -> PipelineState:
        """
        Move the current cycle to another stage.
        """

        if self._current_state is None:
            raise RuntimeError(
                "No active development cycle."
            )

        self._current_state.stage = stage

        return self._current_state

    def complete(self) -> PipelineResult:
        """
        Mark the current cycle as completed.
        """

        if self._current_state is None:
            raise RuntimeError(
                "No active development cycle."
            )

        self._current_state.stage = PipelineStage.COMPLETED

        return PipelineResult(
            success=True,
            state=self._current_state,
            message="Self-development cycle completed.",
        )

    def fail(
        self,
        reason: str,
    ) -> PipelineResult:
        """
        Mark the current cycle as failed.
        """

        if self._current_state is None:
            raise RuntimeError(
                "No active development cycle."
            )

        if not reason.strip():
            raise ValueError(
                "Failure reason cannot be empty."
            )

        self._current_state.metadata["failure_reason"] = reason
        self._current_state.stage = PipelineStage.FAILED

        return PipelineResult(
            success=False,
            state=self._current_state,
            message="Self-development cycle failed.",
        )