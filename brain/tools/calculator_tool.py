import ast
import operator

from brain.tools.base_tool import BaseTool
from brain.tools.tool_result import ToolResult
from brain.tools.tool_schema import ToolSchema


class CalculatorTool(BaseTool):

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return (
            "Performs exact arithmetic calculations such as "
            "addition, subtraction, multiplication, division, "
            "percentages, and powers."
        )
    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
        name=self.name,
        description=self.description,
        parameters={
            "expression": {
                "type": "string",
                "description": "Arithmetic expression to calculate.",
                 "required": True
            }
        }
    )

    def execute(
        self,
        expression: str
    ) -> ToolResult:

        try:

            tree = ast.parse(
                expression,
                mode="eval"
            )

            operators = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
                ast.UAdd: operator.pos,
            }

            def evaluate(node):

                if isinstance(node, ast.Constant):

                    if isinstance(
                        node.value,
                        (int, float)
                    ):
                        return node.value

                    raise ValueError(
                        "Only numbers are allowed."
                    )

                if isinstance(node, ast.BinOp):

                    operation = operators.get(
                        type(node.op)
                    )

                    if operation is None:
                        raise ValueError(
                            "Unsupported operator."
                        )

                    return operation(
                        evaluate(node.left),
                        evaluate(node.right)
                    )

                if isinstance(node, ast.UnaryOp):

                    operation = operators.get(
                        type(node.op)
                    )

                    if operation is None:
                        raise ValueError(
                            "Unsupported operator."
                        )

                    return operation(
                        evaluate(node.operand)
                    )

                raise ValueError(
                    "Unsupported expression."
                )

            result = evaluate(tree.body)

            return ToolResult(
                success=True,
                output=result
            )

        except Exception as exc:

            return ToolResult(
                success=False,
                error=str(exc)
            )