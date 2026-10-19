from brain.ai.intent.intent_service import IntentService
from brain.ai.extraction.extraction_service import ExtractionService
from brain.ai.reasoning.reasoning_service import ReasoningService
from backend.brain.embeddings.embedding_service import EmbeddingService


class AIFactory:

    @staticmethod
    def intent():

        return IntentService()

    @staticmethod
    def extraction():

        return ExtractionService()

    @staticmethod
    def reasoning():

        return ReasoningService()

    @staticmethod
    def embeddings():

        return EmbeddingService()