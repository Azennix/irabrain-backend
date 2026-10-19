from brain.ai.intent.intent_classifier import IntentClassifier
from brain.ai.intent.intent_result import IntentResult


class ModernBERTClassifier(IntentClassifier):

    def classify(
        self,
        text: str
    ) -> IntentResult:

        raise NotImplementedError