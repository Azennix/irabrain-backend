from typing import Any, Protocol

from brain.self_development.intelligence.investigation_request import (
    InvestigationRequest,
)
from brain.self_development.intelligence.foundation_result import (
    FoundationInvestigationResult,
)

class FoundationInvestigationPort(Protocol):
    """
    Minimal port exposed by the existing
    Self-Development Foundation.

    Intelligence depends only on this contract,
    not on Foundation implementation details.
    """

    def investigate(
        self,
        request: InvestigationRequest,
    ) -> FoundationInvestigationResult:
        ...


class SelfDevelopmentFoundationAdapter:
    """
    Adapter between Self-Development Intelligence
    and the existing Self-Development Foundation.

    This keeps the Foundation implementation separate.
    """

    def __init__(
        self,
        foundation: FoundationInvestigationPort,
    ):
        if foundation is None:
            raise ValueError(
                "Self-development foundation cannot be None."
            )

        self.foundation = foundation

    def investigate(
        self,
        request: InvestigationRequest,
    ) -> FoundationInvestigationResult:

        if request is None:
            raise ValueError(
                "Investigation request cannot be None."
            )

        return self.foundation.investigate(request)