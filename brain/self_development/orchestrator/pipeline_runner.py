from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from brain.self_development.orchestrator.self_development_orchestrator import (
    SelfDevelopmentOrchestrator,
    SelfDevelopmentStage,
)
from brain.self_development.orchestrator.stage_controller import (
    StageController,
)
from brain.self_development.orchestrator.pipeline_evidence import (
    PipelineEvidenceCollector,
)
from brain.self_development.validation.test_executor import (
    TestExecutor,
)
from brain.self_development.validation.build_executor import (
    BuildExecutor,
)
from brain.self_development.validation.lint_executor import (
    LintExecutor,
)
from brain.self_development.release.release_controller import (
    ReleaseController,
)
from brain.self_development.release.production_deployer import (
    ProductionDeployer,
)
from brain.self_development.release.rollback_manager import (
    RollbackManager,
)
from brain.self_development.monitoring.health_monitor import HealthStatus
from brain.self_development.monitoring.alert_manager import AlertSeverity

from brain.self_development.monitoring.monitoring_policy import (
    MonitoringPolicy,
)

from brain.self_development.monitoring.monitoring_response_policy import (
    MonitoringResponsePolicy,
)

from brain.self_development.monitoring.decision_gate import (
    DecisionGate,
)

from brain.self_development.monitoring.response_executor import (
    ResponseExecutor,
)
from brain.self_development.policy.capability_policy import (
    CapabilityPolicy,
)
from brain.self_development.security.system_authorization_policy import (
    SystemAuthorizationPolicy,
)


@dataclass(frozen=True)
class PipelineResult:
    """
    Result of a self-development pipeline execution.
    """

    cycle_id: str
    success: bool
    final_stage: SelfDevelopmentStage
    evidence: Dict[str, Any]


class SelfDevelopmentPipeline:
    """
    Coordinates the controlled self-development pipeline.

    This class connects the orchestration state,
    stage controller, and evidence collector.

    It does NOT:
    - directly implement development logic
    - bypass capability policies
    - bypass change policies
    - bypass release policies
    - directly authorize production release
    """

    def __init__(
        self,
        orchestrator: SelfDevelopmentOrchestrator,
        stage_controller: StageController,
        evidence_collector: PipelineEvidenceCollector,
        root_cause_analyzer,
        improvement_planner,
        test_executor: TestExecutor,
        build_executor: BuildExecutor,
        lint_executor: LintExecutor,
        baseline_manager,
        benchmark_runner,
        evaluator,
        regression_detector,
        release_controller: ReleaseController,
        production_deployer: ProductionDeployer,
        rollback_manager: RollbackManager,
        staging_manager,
        canary_manager,
        health_monitor,
        metrics_analyzer,
        alert_manager,
        monitoring_policy: MonitoringPolicy,
        monitoring_response_policy: MonitoringResponsePolicy,
        decision_gate: DecisionGate,
        response_executor: ResponseExecutor,
        workspace_manager,
        development_executor,
        system_authorization_policy: Optional[
            SystemAuthorizationPolicy
        ] = None,
    ):
        if orchestrator is None:
            raise ValueError(
                "Orchestrator cannot be None."
            )

        if stage_controller is None:
            raise ValueError(
                "Stage controller cannot be None."
            )

        if evidence_collector is None:
            raise ValueError(
                "Evidence collector cannot be None."
            )
        if root_cause_analyzer is None:
            raise ValueError(
                "Root cause analyzer cannot be None."
            )

        if improvement_planner is None:
            raise ValueError(
                "Improvement planner cannot be None."
            )
        if test_executor is None:
            raise ValueError(
        "Test executor cannot be None."
    )

        if build_executor is None:
            raise ValueError(
        "Build executor cannot be None."
    )

        if lint_executor is None:
            raise ValueError(
        "Lint executor cannot be None."
    )
        if release_controller is None:
            raise ValueError(
        "Release controller cannot be None."
    )
        if production_deployer is None:
            raise ValueError(
        "Production deployer cannot be None."
    )
        if rollback_manager is None:
            raise ValueError(
        "Rollback manager cannot be None."
    )
        if monitoring_policy is None:
            raise ValueError(
            "Monitoring policy cannot be None."
            )

        if monitoring_response_policy is None:
            raise ValueError(
            "Monitoring response policy cannot be None."
            )

        if decision_gate is None:
            raise ValueError(
            "Decision gate cannot be None."
            )

        if response_executor is None:
            raise ValueError(
            "Response executor cannot be None."
            )
        if workspace_manager is None:
            raise ValueError(
            "Workspace manager cannot be None."
    )

        if development_executor is None:
            raise ValueError(
            "Development executor cannot be None."
    )

        self.orchestrator = orchestrator
        self.stage_controller = stage_controller
        self.evidence_collector = evidence_collector
        self.root_cause_analyzer = root_cause_analyzer
        self.improvement_planner = improvement_planner
        self.test_executor = test_executor
        self.build_executor = build_executor
        self.lint_executor = lint_executor
        self.baseline_manager = baseline_manager
        self.benchmark_runner = benchmark_runner
        self.evaluator = evaluator
        self.regression_detector = regression_detector
        self.release_controller = release_controller
        self.staging_manager = staging_manager
        self.canary_manager = canary_manager
        self.production_deployer = production_deployer
        self.rollback_manager = rollback_manager
        self.health_monitor = health_monitor
        self.metrics_analyzer = metrics_analyzer
        self.alert_manager = alert_manager
        self.monitoring_policy = monitoring_policy
        self.monitoring_response_policy = monitoring_response_policy
        self.decision_gate = decision_gate
        self.response_executor = response_executor
        self.workspace_manager = workspace_manager
        self.development_executor = development_executor
        self.capability_policy = (
            orchestrator.capability_policy
            if orchestrator.capability_policy is not None
            else CapabilityPolicy()
        )
        self.system_authorization_policy = (
            system_authorization_policy
            if system_authorization_policy is not None
            else SystemAuthorizationPolicy()
        )



    def _require_system_authorization(
        self,
        action: str,
    ) -> None:

        decision = self.system_authorization_policy.authorize(
            action
        )

        if not decision.allowed:
            raise PermissionError(
                decision.reason
            )


    def start(

        self,
        improvement_id: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
    ) -> PipelineResult:

        cycle = self.orchestrator.create_cycle(
            improvement_id,
            user_id=user_id,
        )

        if context:
            cycle.context.update(context)

        if self.orchestrator.cycle_repository is not None:
            self.orchestrator.cycle_repository.update_context(
                cycle.cycle_id,
                cycle.context,
        )
            self.orchestrator.cycle_repository.commit()

        self._transition(
            cycle.cycle_id,
            SelfDevelopmentStage.OBSERVATION,
        )



        return self._result(
            cycle.cycle_id
        )

    def investigate(
        self,
        cycle_id: str,
        evidence,
    ) -> PipelineResult:

        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: {cycle_id}"
            )

        self.stage_controller.validate_transition(
            cycle.stage,
            SelfDevelopmentStage.INVESTIGATION,
        )

        if not evidence:
            raise ValueError(
                "Evidence is required for investigation."
            )

        analysis = self.root_cause_analyzer.analyze(
            improvement_id=cycle.improvement_id,
            evidence=evidence,
        )

        self.orchestrator.advance(
            cycle_id,
            SelfDevelopmentStage.INVESTIGATION,
        )

        self.evidence_collector.record(
            cycle_id,
            "investigation",
            {
                "improvement_id": analysis.improvement_id,
                "hypotheses": [
                    {
                        "statement": hypothesis.statement,
                        "confidence": hypothesis.confidence,
                        "supporting_evidence": [
                            item.evidence_id
                            for item in hypothesis.supporting_evidence
                        ],
                    }
                    for hypothesis in analysis.hypotheses
                ],
                "analyzed_at": analysis.analyzed_at.isoformat(),
            },
        )

        return self._result(cycle_id)


    def plan(
        self,
        cycle_id: str,
        analysis,
    ) -> PipelineResult:

        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: {cycle_id}"
            )

        self.stage_controller.validate_transition(
            cycle.stage,
            SelfDevelopmentStage.PLANNING,
        )

        if analysis is None:
            raise ValueError(
                "Root-cause analysis cannot be None."
            )

        if analysis.improvement_id != cycle.improvement_id:
            raise ValueError(
                "Root-cause analysis does not belong "
                "to the current improvement."
            )

        development_plan = self.improvement_planner.create_plan(
            analysis
        )

        self.orchestrator.advance(
            cycle_id,
            SelfDevelopmentStage.PLANNING,
        )

        self.evidence_collector.record(
            cycle_id,
            "planning",
            {
                "plan_id": development_plan.plan_id,
                "improvement_id": development_plan.improvement_id,
                "objective": development_plan.objective,
                "steps": development_plan.steps,
                "constraints": development_plan.constraints,
                "expected_outcome": (
                    development_plan.expected_outcome
                ),
            },
        )

        return self._result(cycle_id)

    def develop(
        self,
        cycle_id: str,
        relative_path: str,
        content: str,
    ) -> PipelineResult:

        self._require_system_authorization("development")
        self._require_capability("development")


        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: {cycle_id}"
            )

        self.stage_controller.validate_transition(
            cycle.stage,
            SelfDevelopmentStage.DEVELOPMENT,
        )

        if not relative_path.strip():
            raise ValueError(
                "Development file path cannot be empty."
            )

        if not isinstance(content, str):
            raise ValueError(
                "Development file content must be a string."
            )

        workspace = self.workspace_manager.create(
            cycle.improvement_id
        )

        development_result = self.development_executor.write_file(
            workspace=workspace,
            relative_path=relative_path,
            content=content,
            improvement_id=cycle.improvement_id,
        )

        self.orchestrator.advance(
            cycle_id,
            SelfDevelopmentStage.DEVELOPMENT,
            context={
                "workspace_id": workspace.workspace_id,
                "workspace_path": workspace.path,
            },
        )

        self.evidence_collector.record(
            cycle_id,
            "development",
            {
                "development_id": (
                    development_result.development_id
                ),
                "improvement_id": (
                    development_result.improvement_id
                ),
                "status": development_result.status.value,
                "workspace": development_result.workspace,
                "changed_files": (
                    development_result.changed_files
                ),
                "details": development_result.details,
            },
        )

        return self._result(cycle_id)

    def advance(
        self,
        cycle_id: str,
        stage: SelfDevelopmentStage,
        result: Any = None,
    ) -> PipelineResult:

        cycle = self.orchestrator.get(
            cycle_id
        )

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: "
                f"{cycle_id}"
            )

        self.stage_controller.validate_transition(
            cycle.stage,
            stage,
        )

        self.orchestrator.advance(
            cycle_id,
            stage,
        )

        if result is not None:
            self.evidence_collector.record(
                cycle_id,
                stage.value,
                result,
            )

        return self._result(
            cycle_id
        )

    def complete(
        self,
        cycle_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> PipelineResult:

        cycle = self.orchestrator.get(
            cycle_id
        )

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: "
                f"{cycle_id}"
            )

        self.stage_controller.validate_transition(
            cycle.stage,
            SelfDevelopmentStage.COMPLETED,
        )

        self.orchestrator.complete(
            cycle_id,
            result,
        )

        if result is not None:
            self.evidence_collector.record(
                cycle_id,
                "completed",
                result,
            )

        return self._result(
            cycle_id
        )

    def fail(
        self,
        cycle_id: str,
        reason: str,
    ) -> PipelineResult:

        cycle = self.orchestrator.get(
            cycle_id
        )

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: "
                f"{cycle_id}"
            )

        self.stage_controller.validate_transition(
            cycle.stage,
            SelfDevelopmentStage.FAILED,
        )

        self.orchestrator.fail(
            cycle_id,
            reason,
        )

        self.evidence_collector.record(
            cycle_id,
            "failed",
            {
                "reason": reason,
            },
        )

        return self._result(
            cycle_id
        )

    def rollback(
        self,
        cycle_id: str,
        candidate_id: str,
        target_version: str,
        reason: str,
    ) -> PipelineResult:
        self._require_system_authorization("rollback")
        self._require_capability("rollback")

        cycle = self.orchestrator.get(
            cycle_id
        )

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: "
                f"{cycle_id}"
            )

        self.stage_controller.validate_transition(
            cycle.stage,
            SelfDevelopmentStage.ROLLED_BACK,
        )

        rollback_result = self.rollback_manager.rollback(
            candidate_id=candidate_id,
            target_version=target_version,
            reason=reason,
    )




        self.evidence_collector.record(
            cycle_id,
            "rolled_back",
            {
                "candidate_id": rollback_result.candidate_id,
                "target_version": rollback_result.target_version,
                "success": rollback_result.success,
                "reason": rollback_result.reason,
                "message": rollback_result.message,
            },
        )
        if not rollback_result.success:
            self.orchestrator.fail(
                cycle_id,
                rollback_result.message,
        )
            self.evidence_collector.record(
            cycle_id,
            "failed",
            {
                "reason": rollback_result.message,
            },
        )
            return self._result(cycle_id)

        self.orchestrator.rollback(
            cycle_id,
            reason,
    )

        return self._result(
            cycle_id
        )



    def lint(
        self,
        cycle_id: str,
        command,
        working_directory: Optional[str] = None,
    ) -> PipelineResult:

        cycle = self.orchestrator.get(
        cycle_id
    )

        if cycle is None:
            raise ValueError(
            f"Self-development cycle not found: "
            f"{cycle_id}"
        )

        self.stage_controller.validate_transition(
            cycle.stage,
            SelfDevelopmentStage.LINTING,
    )

        self.orchestrator.advance(
            cycle_id,
            SelfDevelopmentStage.LINTING,
    )

        lint_result = self.lint_executor.run(
            command=command,
            working_directory=working_directory,
    )

        self.evidence_collector.record(
            cycle_id,
            "linting",
        {
            "success": lint_result.success,
            "command": lint_result.command,
            "return_code": lint_result.return_code,
            "stdout": lint_result.stdout,
            "stderr": lint_result.stderr,
        },
    )

        if not lint_result.success:
            self.orchestrator.fail(
            cycle_id,
            "Candidate failed linting.",
        )

            self.evidence_collector.record(
                cycle_id,
                "failed",
                {
                "reason": "Candidate failed linting.",
                },
            )

        return self._result(
            cycle_id
    )



    def test(
        self,
        cycle_id: str,
        command,
        working_directory: Optional[str] = None,
    ) -> PipelineResult:
        self._require_system_authorization("testing")

        self._require_capability("testing")

        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
            f"Self-development cycle not found: {cycle_id}"
        )

        self.stage_controller.validate_transition(
        cycle.stage,
        SelfDevelopmentStage.TESTING,
    )

        self.orchestrator.advance(
        cycle_id,
        SelfDevelopmentStage.TESTING,
    )

        test_result = self.test_executor.run(
        command=command,
        working_directory=working_directory,
    )

        self.evidence_collector.record(
        cycle_id,
        "testing",
        {
            "success": test_result.success,
            "command": test_result.command,
            "return_code": test_result.return_code,
            "stdout": test_result.stdout,
            "stderr": test_result.stderr,
        },
    )

        if not test_result.success:
            self.orchestrator.fail(
                 cycle_id,
            "Candidate failed testing.",
        )

            self.evidence_collector.record(
                 cycle_id,
                 "failed",
            {
                "reason": "Candidate failed testing.",
            },
        )

        return self._result(cycle_id)


    def build(
        self,
        cycle_id: str,
        command,
        working_directory: Optional[str] = None,
    ) -> PipelineResult:

        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
            f"Self-development cycle not found: {cycle_id}"
        )

        self.stage_controller.validate_transition(
            cycle.stage,
            SelfDevelopmentStage.BUILD,
    )

        self.orchestrator.advance(
            cycle_id,
            SelfDevelopmentStage.BUILD,
    )

        build_result = self.build_executor.run(
            command=command,
            working_directory=working_directory,
    )

        self.evidence_collector.record(
            cycle_id,
            "build",
        {
            "success": build_result.success,
            "command": build_result.command,
            "return_code": build_result.return_code,
            "stdout": build_result.stdout,
            "stderr": build_result.stderr,
        },
    )

        if not build_result.success:
            self.orchestrator.fail(
                cycle_id,
                "Candidate failed build.",
        )

            self.evidence_collector.record(
                cycle_id,
                "failed",
            {
                "reason": "Candidate failed build.",
            },
        )

        return self._result(cycle_id)

    def evaluate(
        self,
        cycle_id: str,
        candidate: Any,
    ) -> PipelineResult:
        self._require_system_authorization("evaluation")
        self._require_capability("evaluation")

        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
            f"Self-development cycle not found: {cycle_id}"
        )

        self.stage_controller.validate_transition(
            cycle.stage,
            SelfDevelopmentStage.EVALUATION,
    )

    # Run registered benchmarks against the candidate.
        benchmark_run = self.benchmark_runner.run(candidate)

        candidate_metrics = {
            result.benchmark_id: result.score
            for result in benchmark_run.results
    }

        if not candidate_metrics:
            raise ValueError(
            "No candidate benchmark metrics available."
        )

    # Find the baseline associated with this cycle.
        baseline_id = cycle.context.get("baseline_id")

        if not baseline_id:
            raise ValueError(
            "Evaluation requires a baseline_id in cycle context."
        )

        baseline = self.baseline_manager.get(baseline_id)

        if baseline is None:
            raise ValueError(
            f"Baseline not found: {baseline_id}"
        )

        evaluation = self.evaluator.evaluate(
            baseline_id=baseline.baseline_id,
            baseline_metrics=baseline.metrics,
            candidate_metrics=candidate_metrics,
    )

        regression_report = self.regression_detector.detect(
            baseline=baseline.metrics,
            candidate=candidate_metrics,
    )

        self.orchestrator.advance(
            cycle_id,
            SelfDevelopmentStage.EVALUATION,
    )

        self.evidence_collector.record(
            cycle_id,
            "evaluation",
        {
                "baseline_id": baseline.baseline_id,
                "candidate_metrics": candidate_metrics,
                "baseline_metrics": baseline.metrics,
                "improved": evaluation.improved,
                "regressed": evaluation.regressed,
                "score_difference": evaluation.score_difference,
                "metric_differences": evaluation.metric_differences,
                "has_regressions": regression_report.has_regressions,
                "regressions": [
                {
                        "capability": regression.capability,
                        "baseline_value": regression.baseline_value,
                        "candidate_value": regression.candidate_value,
                        "difference": regression.difference,
                        "description": regression.description,
                    }
                    for regression in regression_report.regressions
                ],
            },
        )

        return self._result(cycle_id)

    def stage(
        self,
        cycle_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> PipelineResult:

        self._require_system_authorization("staging")
        self._require_capability("staging")



        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: {cycle_id}"
        )

        self.stage_controller.validate_transition(
            cycle.stage,
            SelfDevelopmentStage.STAGING,
    )

    # Candidate ID for the staging environment.
        candidate_id = cycle.context.get(
            "candidate_id",
            cycle.improvement_id,
    )

    # Create isolated staging environment.
        staging = self.staging_manager.create(
            experiment_id=cycle.improvement_id,
            candidate_id=candidate_id,
    )

    # Activate staging environment.
        self.staging_manager.activate(
            staging.staging_id
    )

    # Validate staging result.
        validation_result = (
            result
            if result is not None
            else {
                "success": True,
                "message": "Staging validation completed.",
        }
    )

        staging = self.staging_manager.validate(
            staging.staging_id,
            validation_result,
    )

    # Staging validation failed.
        if staging.status.value != "validated":
            self.orchestrator.fail(
                cycle_id,
                "Staging validation failed.",
        )

            self.evidence_collector.record(
                cycle_id,
                "staging",
            {
                "success": False,
                "staging_id": staging.staging_id,
                "status": staging.status.value,
                "validation": validation_result,
            },
        )
            self.evidence_collector.record(
                cycle_id,
                "failed",
                {
                    "reason": "Staging validation failed.",
                    "stage": "staging",
                },
            )

            return self._result(cycle_id)

    # Store staging information in cycle context.
        cycle.context["staging_id"] = staging.staging_id

        self.orchestrator.advance(
            cycle_id,
            SelfDevelopmentStage.STAGING,
    )

        self.evidence_collector.record(
            cycle_id,
            "staging",
        {
            "success": True,
            "staging_id": staging.staging_id,
            "status": staging.status.value,
            "validation": validation_result,
        },
    )

        return self._result(cycle_id)









    def canary(
        self,
        cycle_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> PipelineResult:
        self._require_system_authorization("canary")

        self._require_capability(
            "canary"
        )

        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: {cycle_id}"
        )

        self.stage_controller.validate_transition(
            cycle.stage,
            SelfDevelopmentStage.CANARY,
    )

        staging_id = cycle.context.get("staging_id")

        if not staging_id:
            raise ValueError(
                "Staging ID is required before canary deployment."
        )

        candidate_id = cycle.context.get(
            "candidate_id",
             cycle.improvement_id,
    )

    # Create controlled canary deployment.
        canary = self.canary_manager.create(
            staging_id=staging_id,
            candidate_id=candidate_id,
    )

    # Activate canary.
        self.canary_manager.activate(
            canary.canary_id
    )

    # Evaluate canary.
        evaluation_result = (
            result
            if result is not None
            else {
                "success": True,
                "message": "Canary evaluation completed.",
        }
    )

        canary = self.canary_manager.evaluate(
            canary.canary_id,
            evaluation_result,
    )

    # Canary evaluation failed.
        if canary.status.value != "passed":
            self.orchestrator.fail(
                cycle_id,
                "Canary evaluation failed.",
        )

            self.evidence_collector.record(
                cycle_id,
                "canary",
            {
                "success": False,
                "canary_id": canary.canary_id,
                "status": canary.status.value,
                "traffic_percentage": (
                    canary.traffic_percentage
                ),
                "metrics": evaluation_result,
            },
        )

            return self._result(cycle_id)

    # Store canary information in cycle context.
        cycle.context["canary_id"] = canary.canary_id

        self.orchestrator.advance(
            cycle_id,
            SelfDevelopmentStage.CANARY,
    )

        self.evidence_collector.record(
            cycle_id,
            "canary",
        {
            "success": True,
            "canary_id": canary.canary_id,
            "status": canary.status.value,
            "traffic_percentage": (
                canary.traffic_percentage
            ),
            "metrics": evaluation_result,
        },
    )

        return self._result(cycle_id)



    def release(
        self,
        cycle_id: str,
        candidate_id: str,
        version: str,
    ) -> PipelineResult:

        self._require_capability(
            "production_release"
        )

        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
          raise ValueError(
            f"Self-development cycle not found: {cycle_id}"
        )

        self.stage_controller.validate_transition(
            cycle.stage,
            SelfDevelopmentStage.RELEASE,
    )

        raw_evidence = self.evidence_collector.get(
            cycle_id
        ).evidence

        testing = raw_evidence.get("testing", {})
        build = raw_evidence.get("build", {})
        linting = raw_evidence.get("linting", {})
        evaluation = raw_evidence.get("evaluation", {})
        staging = raw_evidence.get("staging", {})
        canary = raw_evidence.get("canary", {})

        release_evidence = {
            "tests": testing.get("success") is True,

            "build": build.get("success") is True,

            "lint": linting.get("success") is True,

            "evaluation": (
                evaluation.get("regressed") is False
                and evaluation.get("has_regressions") is False
        ),

            "no_regression": (
                evaluation.get("has_regressions") is False
        ),

           "staging": (
                staging.get("success") is True
                or staging.get("validated") is True
),

            "canary": (
                canary.get("success") is True
                or canary.get("passed") is True
),
    }

        release = self.release_controller.create_release(
            candidate_id=candidate_id,
            version=version,
    )

        decision = self.release_controller.approve_release(
            release_id=release.release_id,
            evidence=release_evidence,
    )

        self.evidence_collector.record(
            cycle_id,
            "release_authorization",
        {
                "release_id": decision.release_id,
                "success": decision.success,
                "status": decision.status,
                "message": decision.message,
                "policy_evidence": release_evidence,
        },
    )

        if not decision.success:
            self.orchestrator.fail(
                cycle_id,
                decision.message,
        )

            self.evidence_collector.record(
                cycle_id,
                "failed",
            {
                    "reason": decision.message,
            },
        )

            return self._result(cycle_id)

        self.orchestrator.advance(
        cycle_id,
        SelfDevelopmentStage.RELEASE,
    )

        deployment = self.production_deployer.deploy(
            release.release_id,
    )

        self.evidence_collector.record(
            cycle_id,
            "production_deployment",
        {
                "release_id": deployment.release_id,
                "success": deployment.success,
                "message": deployment.message,
        },
    )

        if not deployment.success:
            self.release_controller.mark_failed(
                release.release_id,
                evidence={
                    "production_deployment": deployment.message,
            },
        )

            self.orchestrator.fail(
                cycle_id,
                "Production deployment failed.",
        )

            self.evidence_collector.record(
                cycle_id,
                "failed",
            {
                    "reason": "Production deployment failed.",
            },
        )

            return self._result(cycle_id)

        self.release_controller.mark_released(
        release.release_id,
)

        self.orchestrator.complete(
            cycle_id,
)

        self.evidence_collector.record(
            cycle_id,
        "completed",
    {
              "release_id": release.release_id,
              "message": "Production release completed successfully.",
    },
)

        return self._result(cycle_id)


    def health_check(
        self,
        cycle_id: str,
        target_id: str,
        metrics: Dict[str, float],
    ) -> PipelineResult:

        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: {cycle_id}"
        )

        report = self.health_monitor.check(
            target_id=target_id,
            metrics=metrics,
    )

        self.evidence_collector.record(
            cycle_id,
            "health_check",
        {
                "target_id": report.target_id,
                "status": report.status.value,
                "metrics": report.metrics,
                "message": report.message,
        },
    )

        return self._result(cycle_id)

    def analyze_metrics(
        self,
        cycle_id: str,
        target_id: str,
        history: List[Dict[str, float]],
    ) -> PipelineResult:

        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: {cycle_id}"
        )

        analysis = self.metrics_analyzer.analyze(
            target_id=target_id,
            history=history,
    )

        self.evidence_collector.record(
            cycle_id,
            "metrics_analysis",
        {
                "target_id": analysis.target_id,
                "trends": [
                {
                        "metric": trend.metric,
                        "first_value": trend.first_value,
                        "latest_value": trend.latest_value,
                        "difference": trend.difference,
                        "direction": trend.direction,
                }
                    for trend in analysis.trends
            ],
                "degraded_metrics": analysis.degraded_metrics,
        },
    )

        return self._result(cycle_id)


    def create_alert(
        self,
        cycle_id: str,
        target_id: str,
        severity,
        message: str,
        metadata: Optional[Dict] = None,
    ) -> PipelineResult:

        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
                 f"Self-development cycle not found: {cycle_id}"
        )

        alert = self.alert_manager.create(
            target_id=target_id,
            severity=severity,
            message=message,
            metadata=metadata,
    )

        self.evidence_collector.record(
            cycle_id,
            "alert",
        {
                "alert_id": alert.alert_id,
                "target_id": alert.target_id,
                "severity": alert.severity.value,
                "message": alert.message,
                "status": alert.status.value,
                "metadata": alert.metadata,
        },
    )

        return self._result(cycle_id)


    def monitor(
        self,
        cycle_id: str,
        target_id: str,
        metrics: Dict[str, float],
    ) -> PipelineResult:
        self._require_system_authorization("monitoring")

        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: {cycle_id}"
        )

        health_report = self.health_monitor.check(
            target_id=target_id,
            metrics=metrics,
    )

        self.evidence_collector.record(
            cycle_id,
            "health_check",
        {
                "target_id": health_report.target_id,
                "status": health_report.status.value,
                "metrics": health_report.metrics,
                "message": health_report.message,
        },
    )

        if health_report.status.value != "degraded":
            return self._result(cycle_id)

        alert = self.alert_manager.create(
                target_id=target_id,
                severity=AlertSeverity.HIGH,
                message=health_report.message,
                metadata={
                    "source": "health_monitor",
                    "metrics": metrics,
            },
        )

        self.evidence_collector.record(
                cycle_id,
                "alert",
            {
                    "alert_id": alert.alert_id,
                    "target_id": alert.target_id,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "status": alert.status.value,
                    "metadata": alert.metadata,
            },
        )
        monitoring_decision = self.monitoring_policy.evaluate(
            alert
        )
        self.evidence_collector.record(
            cycle_id,
            "monitoring_policy",
            {
                "actionable": monitoring_decision.actionable,
                "reasons": monitoring_decision.reasons,
            },
        )
        response = self.monitoring_response_policy.determine(
            alert
        )

        self.evidence_collector.record(
            cycle_id,
            "monitoring_response_policy",
            {
                "alert_id": response.alert_id,
                "action": response.action.value,
                "reasons": response.reasons,
            },
        )
        gate_decision = self.decision_gate.evaluate(
            monitoring_decision=monitoring_decision,
            response=response,
        )
        self.evidence_collector.record(
            cycle_id,
            "decision_gate",
            {
                "allowed": gate_decision.allowed,
                "action": gate_decision.action,
                "reasons": gate_decision.reasons,
            },
        )
        execution = self.response_executor.execute(
            gate_decision
        )

        self.evidence_collector.record(
            cycle_id,
            "response_execution",
            {
                "success": execution.success,
                "action": execution.action,
                "message": execution.message,
                "executed_at": execution.executed_at.isoformat(),
            },
        )

        return self._result(cycle_id)









    def recover(
        self,
        cycle_id: str,
        candidate_id: str,
        target_version: str,
        reason: str,
    ) -> PipelineResult:

        cycle = self.orchestrator.get(cycle_id)

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: {cycle_id}"
        )

    # Recovery is only allowed from a failed/degraded cycle.
        if cycle.stage not in {
            SelfDevelopmentStage.FAILED,
            SelfDevelopmentStage.ROLLED_BACK,
    }:
            raise ValueError(
                "Recovery requires a failed or rolled-back cycle."
        )

        rollback_result = self.rollback_manager.rollback(
            candidate_id=candidate_id,
            target_version=target_version,
            reason=reason,
    )

        self.evidence_collector.record(
            cycle_id,
            "recovery",
        {
                "success": rollback_result.success,
                "candidate_id": rollback_result.candidate_id,
                "target_version": rollback_result.target_version,
                "reason": rollback_result.reason,
                "message": rollback_result.message,
        },
    )

        if rollback_result.success:
            if cycle.stage == SelfDevelopmentStage.FAILED:
                self.orchestrator.advance(
                    cycle_id,
                    SelfDevelopmentStage.ROLLED_BACK,
            )

        return self._result(cycle_id)

    def _require_capability(
        self,
        capability: str,
    ) -> None:
        if not self.capability_policy.is_allowed(
            capability
        ):
            raise PermissionError(
                f"Capability blocked by policy: "
                f"{capability}"
            )





    def _transition(
        self,
        cycle_id: str,
        target_stage: SelfDevelopmentStage,
    ) -> None:

        cycle = self.orchestrator.get(
            cycle_id
        )

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: "
                f"{cycle_id}"
            )

        self.stage_controller.validate_transition(
            cycle.stage,
            target_stage,
        )

        self.orchestrator.advance(
            cycle_id,
            target_stage,
        )

    def _result(
        self,
        cycle_id: str,
    ) -> PipelineResult:

        cycle = self.orchestrator.get(
            cycle_id
        )

        if cycle is None:
            raise ValueError(
                f"Self-development cycle not found: "
                f"{cycle_id}"
            )

        evidence = self.evidence_collector.get(
            cycle_id
        )

        return PipelineResult(
            cycle_id=cycle_id,
            success=(
                cycle.stage
                == SelfDevelopmentStage.COMPLETED
            ),
            final_stage=cycle.stage,
            evidence=evidence.evidence,
        )