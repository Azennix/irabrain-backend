from brain.tools.tool_call import ToolCall
from brain.tools.tool_registry import ToolRegistry


class ToolCallValidator:

    """
    Validates a ToolCall against the selected tool's schema.

    It does NOT:
    - select a tool
    - extract arguments
    - execute a tool
    - handle permissions

    It only verifies that the ToolCall matches
    the registered tool's input contract.
    """

    def __init__(
        self,
        registry: ToolRegistry
    ):
        self.registry = registry

    def validate(
        self,
        call: ToolCall
    ) -> bool:

        # ==========================================
        # TOOL EXISTS
        # ==========================================

        tool = self.registry.get(
            call.tool_name
        )

        if tool is None:
            return False

        schema = tool.schema

        # ==========================================
        # VALID ARGUMENT NAMES
        # ==========================================

        allowed_parameters = set(
            schema.parameters.keys()
        )

        provided_parameters = set(
            call.arguments.keys()
        )

        if not provided_parameters.issubset(
            allowed_parameters
        ):
            return False

        # ==========================================
        # REQUIRED PARAMETERS
        # ==========================================

        for parameter_name in allowed_parameters:

            parameter = schema.parameters[
                parameter_name
            ]

            if parameter.get(
                "required",
                False
            ):

                if parameter_name not in call.arguments:
                    return False

        return True