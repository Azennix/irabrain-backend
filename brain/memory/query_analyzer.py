from brain.llm.memory_llm_service import MemoryLLMService
from brain.llm.prompt_builder import PromptBuilder
from brain.memory.memory_query import MemoryQuery


class MemoryQueryAnalyzer:

    def __init__(
        self,
        llm_service: MemoryLLMService
    ):
        self.llm_service = llm_service