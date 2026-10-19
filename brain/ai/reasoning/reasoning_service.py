from brain.ai.base_ai_service import BaseAIService


class ReasoningService(BaseAIService):

    def generate(
        self,
        prompt: str
    ):
        raise NotImplementedError