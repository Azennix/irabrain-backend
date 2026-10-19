from abc import ABC, abstractmethod

from brain.tools.tool_result import ToolResult
from brain.tools.tool_schema import ToolSchema


class BaseTool(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def schema(self) -> ToolSchema:
        pass

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass