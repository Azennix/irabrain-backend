from brain.tools.tool_decision import ToolDecision
from brain.tools.tool_execution_policy import ToolExecutionPolicy
from brain.tools.tool_permission import ToolPermission
from brain.tools.tool_registry import ToolRegistry
from brain.tools.tool_result import ToolResult
from brain.tools.tool_validator import ToolValidator
from brain.tools.tool_pipeline_result import ToolPipelineResult
from brain.tools.tool_call_validator import ToolCallValidator


class ToolPipeline:

    """
    Coordinates the complete tool lifecycle.

    Flow:

        ToolDecision
             ↓
        Decision Validation
             ↓
        ToolCall Validation
             ↓
        Execution Policy
             ↓
        Permission / Safety
             ↓
        ToolExecutor
             ↓
        ToolPipelineResult
    """

    def __init__(
        self,
        registry: ToolRegistry,
        executor
    ):
        self.registry = registry
        self.executor = executor

        self.validator = ToolValidator(
            registry
        )

        self.call_validator = ToolCallValidator(
            registry
        )

        self.permission = ToolPermission()

    def execute(
        self,
        decision: ToolDecision,
        call=None,
        policy: ToolExecutionPolicy | None = None
    ) -> ToolPipelineResult:

        # ==========================================
        # NO TOOL REQUIRED
        # ==========================================

        if not decision.requires_tool:

            return ToolPipelineResult(
                decision=decision,
                executed=False
            )

        # ==========================================
        # DECISION VALIDATION
        # ==========================================

        if not self.validator.validate(
            decision
        ):

            return ToolPipelineResult(
                decision=decision,
                policy=policy,
                result=ToolResult(
                    success=False,
                    error="Tool decision is invalid."
                ),
                executed=False
            )

        # ==========================================
        # TOOL CALL REQUIRED
        # ==========================================

        if call is None:

            return ToolPipelineResult(
                decision=decision,
                policy=policy,
                result=ToolResult(
                    success=False,
                    error="Tool call is missing."
                ),
                executed=False
            )

        # ==========================================
        # TOOL CALL VALIDATION
        # ==========================================

        if not self.call_validator.validate(
            call
        ):

            return ToolPipelineResult(
                decision=decision,
                policy=policy,
                result=ToolResult(
                    success=False,
                    error="Tool call is invalid."
                ),
                executed=False
            )

        # ==========================================
        # DEFAULT POLICY
        # ==========================================

        if policy is None:

            policy = ToolExecutionPolicy()

        # ==========================================
        # PERMISSION / SAFETY
        # ==========================================

        policy = self.permission.check(
            policy
        )

        if not policy.allowed:

            return ToolPipelineResult(
                decision=decision,
                policy=policy,
                result=ToolResult(
                    success=False,
                    error=(
                        policy.reason
                        or "Tool execution is not allowed."
                    )
                ),
                executed=False
            )

        # ==========================================
        # USER CONFIRMATION
        # ==========================================

        if policy.requires_confirmation:

            return ToolPipelineResult(
                decision=decision,
                policy=policy,
                result=ToolResult(
                    success=False,
                    error="User confirmation is required."
                ),
                executed=False
            )

        # ==========================================
        # EXECUTION
        # ==========================================

        result = self.executor.execute(
            call.tool_name,
            **call.arguments
        )

        # ==========================================
        # FINAL RESULT
        # ==========================================

        return ToolPipelineResult(
            decision=decision,
            policy=policy,
            result=result,
            executed=True
        )