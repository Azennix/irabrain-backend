from brain.self_development.integration.self_development_gateway import (
    SelfDevelopmentGateway,
)
from brain.self_development.intelligence.foundation_adapter import (
    SelfDevelopmentFoundationAdapter,
)
from brain.self_development.intelligence.safe_investigation_pipeline import (
    SafeSelfDevelopmentInvestigationPipeline,
)
from brain.self_development.investigation.investigation_service import (
    SelfDevelopmentInvestigationService,
)


def create_self_development_gateway() -> SelfDevelopmentGateway:
    """
    Create the production Self-Development gateway.

    This is the composition boundary between the
    Core Integration layer and the separate
    Self-Development system.
    """

    foundation_service = SelfDevelopmentInvestigationService()

    foundation_adapter = SelfDevelopmentFoundationAdapter(
        foundation=foundation_service,
    )

    investigation_pipeline = (
        SafeSelfDevelopmentInvestigationPipeline(
            foundation_adapter=foundation_adapter,
        )
    )

    return SelfDevelopmentGateway(
        investigation_pipeline=investigation_pipeline,
    )