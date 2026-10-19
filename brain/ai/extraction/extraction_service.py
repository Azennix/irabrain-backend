from brain.ai.base_ai_service import BaseAIService


class ExtractionService(BaseAIService):

    def generate(
        self,
        prompt: str
    ):
        raise NotImplementedError