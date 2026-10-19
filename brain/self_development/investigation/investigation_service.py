from typing import Any

from brain.self_development.domain.models import Evidence
from brain.self_development.investigation.evidence_collector import (
    EvidenceCollector,
)
from brain.self_development.investigation.repository_analyzer import (
    RepositoryAnalyzer,
    RepositorySnapshot,
)
from brain.self_development.investigation.root_cause_analyzer import (
    RootCauseAnalysis,
    RootCauseAnalyzer,
)
from brain.self_development.intelligence.investigation_request import (
    InvestigationRequest,
)
from brain.self_development.intelligence.foundation_result import (
    FoundationInvestigationResult,
)


class SelfDevelopmentInvestigationService:
    """
    Foundation-side investigation service.

    Composes the existing investigation components:

    - EvidenceCollector
    - RepositoryAnalyzer
    - RootCauseAnalyzer

    It does not:
    - modify source code
    - execute development
    - run tests
    - deploy changes
    - make release decisions
    - grant authorization
    """

    def __init__(
        self,
        evidence_collector: EvidenceCollector | None = None,
        repository_analyzer: RepositoryAnalyzer | None = None,
        root_cause_analyzer: RootCauseAnalyzer | None = None,
    ):
        self.evidence_collector = (
            evidence_collector
            or EvidenceCollector()
        )

        self.repository_analyzer = (
            repository_analyzer
            or RepositoryAnalyzer()
        )

        self.root_cause_analyzer = (
            root_cause_analyzer
            or RootCauseAnalyzer()
        )

    def investigate(
        self,
        request: InvestigationRequest,
    ) -> FoundationInvestigationResult:

        if request is None:
            raise ValueError(
                "Investigation request cannot be None."
            )

        improvement_id = request.observation_id

        try:
            collected_evidence = []

            for source, description, data in self._build_evidence(
                request
            ):
                evidence = self.evidence_collector.collect(
                    improvement_id=improvement_id,
                    source=source,
                    description=description,
                    data=data,
                )

                collected_evidence.append(evidence)

            if not collected_evidence:
                return FoundationInvestigationResult(
                    success=False,
                    status="no_evidence",
                    evidence={},
                    error="No investigation evidence was collected.",
                )

            analysis = self.root_cause_analyzer.analyze(
                improvement_id=improvement_id,
                evidence=collected_evidence,
            )

            return FoundationInvestigationResult(
                success=True,
                status="completed",
                evidence={
                    "improvement_id": (
                        analysis.improvement_id
                    ),
                    "evidence": [
                        self._serialize_evidence(item)
                        for item in collected_evidence
                    ],
                    "hypotheses": [
                        {
                            "statement": hypothesis.statement,
                            "confidence": hypothesis.confidence,
                            "supporting_evidence": [
                                item.evidence_id
                                for item in (
                                    hypothesis.supporting_evidence
                                )
                            ],
                        }
                        for hypothesis in analysis.hypotheses
                    ],
                    "analyzed_at": (
                        analysis.analyzed_at.isoformat()
                    ),
                },
            )

        except Exception as error:
            return FoundationInvestigationResult(
                success=False,
                status="failed",
                evidence={},
                error=str(error),
            )

    def _build_evidence(
        self,
        request: InvestigationRequest,
    ) -> list[tuple[str, str, Any]]:

        evidence_items: list[
            tuple[str, str, Any]
        ] = []

        if request.evidence:
            evidence_items.append(
                (
                    "core_signal",
                    "Evidence received from IRABRAIN Core.",
                    dict(request.evidence),
                )
            )

        repository_root = request.evidence.get(
            "repository_root"
        )

        if repository_root:
            snapshot = self.repository_analyzer.analyze(
                repository_root
            )

            evidence_items.append(
                (
                    "repository_analyzer",
                    "Repository structure analyzed.",
                    self._serialize_repository_snapshot(
                        snapshot
                    ),
                )
            )

        return evidence_items

    @staticmethod
    def _serialize_evidence(
        evidence: Evidence,
    ) -> dict[str, Any]:

        return {
            "evidence_id": evidence.evidence_id,
            "source": evidence.source,
            "description": evidence.description,
            "data": dict(evidence.data),
            "collected_at": (
                evidence.collected_at.isoformat()
            ),
        }

    @staticmethod
    def _serialize_repository_snapshot(
        snapshot: RepositorySnapshot,
    ) -> dict[str, Any]:

        return {
            "root": snapshot.root,
            "files": [
                {
                    "path": item.path,
                    "file_type": item.file_type,
                    "size_bytes": item.size_bytes,
                }
                for item in snapshot.files
            ],
        }