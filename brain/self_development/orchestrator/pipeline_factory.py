from brain.self_development.investigation.evidence_collector import (
    EvidenceCollector,
)
from brain.self_development.investigation.root_cause_analyzer import (
    RootCauseAnalyzer,
)
from brain.self_development.planning.improvement_planner import (
    ImprovementPlanner,
)

from brain.self_development.development.workspace_manager import (
    WorkspaceManager,
)
from brain.self_development.development.development_executor import (
    DevelopmentExecutor,
)
from brain.self_development.development.code_change_manager import (
    CodeChangeManager,
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

from brain.self_development.evaluation.baseline_manager import (
    BaselineManager,
)
from brain.self_development.evaluation.benchmark_runner import (
    BenchmarkRunner,
)
from brain.self_development.evaluation.evaluator import (
    Evaluator,
)
from brain.self_development.validation.regression_detector import (
    RegressionDetector,
)

from brain.self_development.policy.capability_policy import (
    CapabilityPolicy,
)
from brain.self_development.policy.change_policy import (
    ChangePolicy,
)
from brain.self_development.policy.release_policy import (
    ReleasePolicy,
)

from brain.self_development.release.staging_manager import (
    StagingManager,
)
from brain.self_development.release.canary_manager import (
    CanaryManager,
)
from brain.self_development.release.rollback_manager import (
    RollbackManager,
)
from brain.self_development.release.release_manager import (
    ReleaseManager,
)
from brain.self_development.release.release_controller import (
    ReleaseController,
)
from brain.self_development.release.production_deployer import (
    ProductionDeployer,
)

from brain.self_development.versioning.version_manager import (
    VersionManager,
)
from brain.self_development.versioning.version_registry import (
    VersionRegistry,
)

from brain.self_development.monitoring.health_monitor import (
    HealthMonitor,
)
from brain.self_development.monitoring.metrics_analyzer import (
    MetricsAnalyzer,
)
from brain.self_development.monitoring.alert_manager import (
    AlertManager,
)

from brain.self_development.orchestrator.self_development_components import (
    SelfDevelopmentComponents,
)
from brain.self_development.orchestrator.self_development_orchestrator import (
    SelfDevelopmentOrchestrator,
)
from brain.self_development.orchestrator.stage_controller import (
    StageController,
)
from brain.self_development.orchestrator.pipeline_evidence import (
    PipelineEvidenceCollector,
)
from brain.self_development.orchestrator.pipeline_runner import (
    SelfDevelopmentPipeline,

)
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
from brain.self_development.persistence.self_development_cycle_repository import (
    SelfDevelopmentCycleRepository,
)
from brain.self_development.persistence.system_identity_repository import (
    SystemIdentityRepository,
)

from brain.self_development.security.system_authorization_policy import (
    SystemAuthorizationPolicy,
)
from brain.self_development.audit.audit_service import AuditService
from brain.self_development.persistence.audit_event_repository import (
    AuditEventRepository,
)


def create_self_development_components(

):
    """
    Create and wire all self-development components.

    This function only constructs dependencies.
    It does not execute a development cycle.
    """

    workspace_manager = WorkspaceManager()

    components = SelfDevelopmentComponents(
        evidence_collector=EvidenceCollector(),
        root_cause_analyzer=RootCauseAnalyzer(),
        improvement_planner=ImprovementPlanner(),

        workspace_manager=workspace_manager,
        development_executor=DevelopmentExecutor(
            workspace_manager
        ),
        code_change_manager=CodeChangeManager(),

        test_executor=TestExecutor(),
        build_executor=BuildExecutor(),
        lint_executor=LintExecutor(),

        baseline_manager=BaselineManager(),
        benchmark_runner=BenchmarkRunner(),
        evaluator=Evaluator(),
        regression_detector=RegressionDetector(),

        capability_policy=CapabilityPolicy(),
        change_policy=ChangePolicy(),
        release_policy=ReleasePolicy(),

        staging_manager=StagingManager(),
        canary_manager=CanaryManager(),

        rollback_manager=RollbackManager(),
        release_manager=ReleaseManager(),

        version_manager=VersionManager(),
        version_registry=VersionRegistry(),

        health_monitor=HealthMonitor(),
        metrics_analyzer=MetricsAnalyzer(),
        alert_manager=AlertManager(),

        monitoring_policy=MonitoringPolicy(),
        monitoring_response_policy=MonitoringResponsePolicy(),
        decision_gate=DecisionGate(),
        response_executor=ResponseExecutor(),

    )

    components.validate()

    return components


def create_self_development_pipeline(
        cycle_repository=None,
):
    """
    Create the complete self-development pipeline.

    Returns a ready-to-use pipeline without
    automatically executing anything.
    """

    components = create_self_development_components()

    release_controller = ReleaseController(
        release_policy=components.release_policy,
        release_manager=components.release_manager,
    )
    system_identity_repository = None

    if cycle_repository is not None:
        system_identity_repository = SystemIdentityRepository(
        cycle_repository.db
    )

    audit_service = None

    if cycle_repository is not None:
        audit_event_repository = AuditEventRepository(
            cycle_repository.db
    )

        audit_service = AuditService(
            audit_event_repository
    )

    system_authorization_policy = (
        SystemAuthorizationPolicy()
)



    orchestrator = SelfDevelopmentOrchestrator(
        capability_policy=components.capability_policy,
        change_policy=components.change_policy,
        release_policy=components.release_policy,
        cycle_repository=cycle_repository,
        system_identity_repository=system_identity_repository,
        system_authorization_policy=system_authorization_policy,
        audit_service=audit_service,
    )

    stage_controller = StageController()

    evidence_collector = PipelineEvidenceCollector()

    pipeline = SelfDevelopmentPipeline(
        orchestrator=orchestrator,
        stage_controller=stage_controller,
        evidence_collector=evidence_collector,

        root_cause_analyzer=components.root_cause_analyzer,
        improvement_planner=components.improvement_planner,

        test_executor=components.test_executor,
        build_executor=components.build_executor,
        lint_executor=components.lint_executor,

        baseline_manager=components.baseline_manager,
        benchmark_runner=components.benchmark_runner,
        evaluator=components.evaluator,
        regression_detector=components.regression_detector,

        release_controller=release_controller,
        production_deployer=ProductionDeployer(),
        rollback_manager=components.rollback_manager,
        staging_manager=components.staging_manager,
        canary_manager=components.canary_manager,
        health_monitor=components.health_monitor,
        metrics_analyzer=components.metrics_analyzer,
        alert_manager=components.alert_manager,

        monitoring_policy=components.monitoring_policy,
        monitoring_response_policy=components.monitoring_response_policy,
        decision_gate=components.decision_gate,
        response_executor=components.response_executor,

        workspace_manager=components.workspace_manager,
        development_executor=components.development_executor,
        system_authorization_policy=system_authorization_policy
    )



    return pipeline