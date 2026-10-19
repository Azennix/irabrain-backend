from dataclasses import dataclass


@dataclass
class SelfDevelopmentComponents:
    """
    Holds the components used by the IRABRAIN
    self-development subsystem.

    This is a dependency container only.
    It does not execute the pipeline.
    """

    evidence_collector: object
    root_cause_analyzer: object
    improvement_planner: object

    workspace_manager: object
    development_executor: object
    code_change_manager: object

    test_executor: object
    build_executor: object
    lint_executor: object

    baseline_manager: object
    benchmark_runner: object
    evaluator: object
    regression_detector: object

    capability_policy: object
    change_policy: object
    release_policy: object

    staging_manager: object
    canary_manager: object

    rollback_manager: object
    release_manager: object

    version_manager: object
    version_registry: object

    health_monitor: object
    metrics_analyzer: object
    alert_manager: object

    monitoring_policy: object
    monitoring_response_policy: object
    decision_gate: object
    response_executor: object


    def validate(self) -> None:
        """
        Validate that all required components exist.
        """

        required_components = {
            "evidence_collector": self.evidence_collector,
            "root_cause_analyzer": self.root_cause_analyzer,
            "improvement_planner": self.improvement_planner,
            "workspace_manager": self.workspace_manager,
            "development_executor": self.development_executor,
            "code_change_manager": self.code_change_manager,
            "test_executor": self.test_executor,
            "build_executor": self.build_executor,
            "lint_executor": self.lint_executor,
            "baseline_manager": self.baseline_manager,
            "benchmark_runner": self.benchmark_runner,
            "evaluator": self.evaluator,
            "regression_detector": self.regression_detector,
            "capability_policy": self.capability_policy,
            "change_policy": self.change_policy,
            "release_policy": self.release_policy,
            "staging_manager": self.staging_manager,
            "canary_manager": self.canary_manager,
            "rollback_manager": self.rollback_manager,
            "release_manager": self.release_manager,
            "version_manager": self.version_manager,
            "version_registry": self.version_registry,
            "health_monitor": self.health_monitor,
            "metrics_analyzer": self.metrics_analyzer,
            "alert_manager": self.alert_manager,
            "monitoring_policy": self.monitoring_policy,
            "monitoring_response_policy": self.monitoring_response_policy,
            "decision_gate": self.decision_gate,
            "response_executor": self.response_executor,

        }

        missing = [
            name
            for name, component in required_components.items()
            if component is None
        ]

        if missing:
            raise ValueError(
                "Missing self-development components: "
                + ", ".join(missing)
            )