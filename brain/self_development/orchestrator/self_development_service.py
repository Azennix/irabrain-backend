from dataclasses import dataclass
from typing import Any, Dict, Optional

from brain.self_development.orchestrator.pipeline_runner import (
    PipelineResult,
    SelfDevelopmentPipeline,
)


@dataclass(frozen=True)
class SelfDevelopmentRequest:
    """
    Request sent from the main Brain Orchestrator
    to the self-development subsystem.
    """

    improvement_id: str
    context: Dict[str, Any]


class SelfDevelopmentService:
    """
    Public service interface for IRABRAIN self-development.

    The main Brain Orchestrator should communicate with
    the self-development subsystem through this service
    instead of directly controlling internal components.

    It does NOT:
    - bypass policies
    - directly modify production code
    - independently authorize releases
    - replace the self-development pipeline
    """

    def __init__(
        self,
        pipeline: SelfDevelopmentPipeline,
    ):
        if pipeline is None:
            raise ValueError(
                "Self-development pipeline cannot be None."
            )

        self.pipeline = pipeline

    def start(
        self,
        request: SelfDevelopmentRequest,
    ) -> PipelineResult:

        if request is None:
            raise ValueError(
                "Self-development request cannot be None."
            )

        if not request.improvement_id.strip():
            raise ValueError(
                "Improvement ID cannot be empty."
            )

        return self.pipeline.start(
            improvement_id=request.improvement_id,
            context=dict(request.context),
        )

    def advance(
        self,
        cycle_id: str,
        stage,
        result: Optional[Any] = None,
    ) -> PipelineResult:

        if not cycle_id.strip():
            raise ValueError(
                "Cycle ID cannot be empty."
            )

        return self.pipeline.advance(
            cycle_id=cycle_id,
            stage=stage,
            result=result,
        )

    def complete(
        self,
        cycle_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> PipelineResult:

        if not cycle_id.strip():
            raise ValueError(
                "Cycle ID cannot be empty."
            )

        return self.pipeline.complete(
            cycle_id=cycle_id,
            result=result,
        )

    def fail(
        self,
        cycle_id: str,
        reason: str,
    ) -> PipelineResult:

        if not cycle_id.strip():
            raise ValueError(
                "Cycle ID cannot be empty."
            )

        return self.pipeline.fail(
            cycle_id=cycle_id,
            reason=reason,
        )

    def rollback(
        self,
        cycle_id: str,
        reason: str,
    ) -> PipelineResult:

        if not cycle_id.strip():
            raise ValueError(
                "Cycle ID cannot be empty."
            )

        return self.pipeline.rollback(
            cycle_id=cycle_id,
            reason=reason,
        )