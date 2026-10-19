from brain.tools.tool_execution_policy import ToolExecutionPolicy


class ToolPermission:

    """
    Determines whether a tool execution is permitted.

    It does NOT execute the tool.
    It only applies permission and safety rules.
    """

    def check(
        self,
        policy: ToolExecutionPolicy
    ) -> ToolExecutionPolicy:

        if not policy.allowed:

            return ToolExecutionPolicy(
                allowed=False,
                requires_confirmation=policy.requires_confirmation,
                risk_level=policy.risk_level,
                reason=policy.reason or "Tool execution is not allowed."
            )

        if policy.risk_level in {
            "high",
            "critical"
        }:

            return ToolExecutionPolicy(
                allowed=True,
                requires_confirmation=True,
                risk_level=policy.risk_level,
                reason=(
                    policy.reason
                    or "User confirmation is required for this operation."
                )
            )

        return policy