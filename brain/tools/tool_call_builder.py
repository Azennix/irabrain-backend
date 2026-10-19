from brain.base.brain_request import BrainRequest
from brain.tools.tool_argument_extractor import ToolArgumentExtractor
from brain.tools.tool_call import ToolCall
from brain.tools.tool_decision import ToolDecision


class ToolCallBuilder:

    """
    Builds a ToolCall from a ToolDecision and user request.

    It does not:
    - select tools
    - execute tools
    - validate calls
    - handle permissions
    """

    def __init__(
        self,
        extractor: ToolArgumentExtractor
    ):
        self.extractor = extractor

    def build(
        self,
        request: BrainRequest,
        decision: ToolDecision
    ) -> ToolCall | None:

        return self.extractor.extract(
            request,
            decision
        )