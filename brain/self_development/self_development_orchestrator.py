from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class SelfDevelopmentResult:
    """
    Structured result of a self-development cycle.
    """

    improvement_id: str
    success: bool
    stage: str
    message: str

    evidence_count: int = 0
    plan_steps: int = 0

    development_id: Optional[str] = None
    workspace_id: Optional[str] = None

    completed_at: datetime = field(
        default_factory=datetime.utcnow
    )


class SelfDevelopmentOrchestrator:
    """
    Coordinates the IRABRAIN self-development pipeline.

    Current pipeline:

        Evidence
            ↓
        Root Cause Analysis
            ↓
        Improvement Planning
            ↓
        Isolated Workspace
            ↓
        Controlled Development
            ↓
        Testing

    Responsibilities:
    - coordinate self-development stages
    - maintain pipeline flow
    - connect existing self-development components
    - stop the pipeline when a stage fails
    - return structured pipeline results

    It does NOT:
    - bypass capability policy
    - directly modify production code
    - automatically release production changes
    - perform unrestricted deployment
    - make final production release decisions
    """

    def __init__(
        self,
        evidence_collector,
        root_cause_analyzer,
        improvement_planner,
        workspace_manager,
        development_executor,
        test_executor,
        build_executor,
    ):
        self.evidence_collector = (
            evidence_collector
        )

        self.root_cause_analyzer = (
            root_cause_analyzer
        )

        self.improvement_planner = (
            improvement_planner
        )

        self.workspace_manager = (
            workspace_manager
        )

        self.development_executor = (
            development_executor
        )

        self.test_executor = (
            test_executor
        )
        self.build_executor = (
            build_executor
        )

    def run(
        self,
        improvement_id: str,
        evidence_input: Dict[str, Any],
        candidate_path: str,
        candidate_content: str,
    ) -> SelfDevelopmentResult:

        if not improvement_id.strip():
            raise ValueError(
                "Improvement ID cannot be empty."
            )

        if evidence_input is None:
            raise ValueError(
                "Evidence input cannot be None."
            )

        if not candidate_path.strip():
            raise ValueError(
                "Candidate path cannot be empty."
            )

        if not isinstance(
            candidate_content,
            str,
        ):
            raise ValueError(
                "Candidate content must be a string."
            )

        # -------------------------------------------------
        # Stage 1: Evidence
        # -------------------------------------------------

        self.evidence_collector.collect(
            improvement_id=improvement_id,
            source=evidence_input.get(
                "source",
                "unknown",
            ),
            description=evidence_input.get(
                "description",
                "Self-development evidence.",
            ),
            data=evidence_input.get(
                "data",
                {},
            ),
        )

        collected = (
            self.evidence_collector
            .get_for_improvement(
                improvement_id
            )
        )

        # -------------------------------------------------
        # Stage 2: Root Cause Analysis
        # -------------------------------------------------

        analysis = (
            self.root_cause_analyzer.analyze(
                improvement_id=improvement_id,
                evidence=collected,
            )
        )

        # -------------------------------------------------
        # Stage 3: Improvement Planning
        # -------------------------------------------------

        plan = (
            self.improvement_planner.create_plan(
                analysis
            )
        )

        # -------------------------------------------------
        # Stage 4: Isolated Workspace
        # -------------------------------------------------

        workspace = (
            self.workspace_manager.create(
                improvement_id
            )
        )

        # -------------------------------------------------
        # Stage 5: Controlled Development
        # -------------------------------------------------

        development = (
            self.development_executor.write_file(
                workspace=workspace,
                relative_path=candidate_path,
                content=candidate_content,
            )
        )

        # -------------------------------------------------
        # Stage 6: Testing
        # -------------------------------------------------

        test_result = (
            self.test_executor.run(
                command=[
                    "python",
                    "-m",
                    "py_compile",
                    candidate_path,
                ],
                working_directory=workspace.path,
            )
        )

        if not test_result.success:

            return SelfDevelopmentResult(
                improvement_id=improvement_id,
                success=False,
                stage="testing",
                message=(
                    "Candidate failed testing."
                ),
                evidence_count=len(
                    collected
                ),
                plan_steps=len(
                    plan.steps
                ),
                development_id=(
                    development.development_id
                ),
                workspace_id=(
                    workspace.workspace_id
                ),
            )

                # -------------------------------------------------
        # Stage 7: Build
        # -------------------------------------------------

        build_result = (
            self.build_executor.run(
                command=[
                    "python",
                    "-m",
                    "compileall",
                    ".",
                ],
                working_directory=workspace.path,
            )
        )

        if not build_result.success:

            return SelfDevelopmentResult(
                improvement_id=improvement_id,
                success=False,
                stage="build",
                message=(
                    "Candidate failed build."
                ),
                evidence_count=len(
                    collected
                ),
                plan_steps=len(
                    plan.steps
                ),
                development_id=(
                    development.development_id
                ),
                workspace_id=(
                    workspace.workspace_id
                ),
            )

        # -------------------------------------------------
        # Pipeline completed successfully
        # -------------------------------------------------

        return SelfDevelopmentResult(
            improvement_id=improvement_id,
            success=True,
            stage="build",
            message=(
                "Candidate passed controlled "
                "development and testing, and building."
            ),
            evidence_count=len(
                collected
            ),
            plan_steps=len(
                plan.steps
            ),
            development_id=(
                development.development_id
            ),
            workspace_id=(
                workspace.workspace_id
            ),
        )