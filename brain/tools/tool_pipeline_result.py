from dataclasses import dataclass

from brain.tools.tool_decision import ToolDecision
from brain.tools.tool_execution_policy import ToolExecutionPolicy
from brain.tools.tool_result import ToolResult


@dataclass(slots=True)
class ToolPipelineResult:
    decision: ToolDecision

    policy: ToolExecutionPolicy | None = None

    result: ToolResult | None = None

    executed: bool = False