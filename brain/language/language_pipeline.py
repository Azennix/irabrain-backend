from brain.language.language_detector import LanguageDetector
from brain.language.language_policy import LanguagePolicyEngine
from brain.language.language_processor import LanguageProcessor
from brain.language.language_response_formatter import (
    LanguageResponseFormatter
)


class LanguagePipeline:

    """
    Language processing pipeline for IRABrain.

    IMPORTANT:

    Language detection is already performed by
    MessageAnalyzer.

    Therefore this pipeline does NOT make an LLM call
    for language detection.

    Flow:

        MessageAnalyzer
              ↓
        LanguageDetector.from_analysis()
              ↓
        LanguagePolicyEngine
              ↓
        LanguageProcessor
              ↓
        LanguageResponseFormatter
    """

    def __init__(
        self,
        detector=None,
        policy_engine=None,
        processor=None,
        formatter=None
    ):

        # ==========================================
        # LANGUAGE DETECTOR
        # ==========================================

        self.detector = (
            detector
            or LanguageDetector()
        )

        # ==========================================
        # LANGUAGE POLICY
        # ==========================================

        self.policy_engine = (
            policy_engine
            or LanguagePolicyEngine()
        )

        # ==========================================
        # LANGUAGE PROCESSOR
        # ==========================================

        self.processor = (
            processor
            or LanguageProcessor()
        )

        # ==========================================
        # RESPONSE FORMATTER
        # ==========================================

        self.formatter = (
            formatter
            or LanguageResponseFormatter()
        )

    # =================================================
    # PREPARE LANGUAGE
    # =================================================

    def prepare(
        self,
        text: str,
        analysis: dict
    ):

        # ---------------------------------------------
        # 1. Convert MessageAnalyzer output
        #    into LanguageProfile
        # ---------------------------------------------

        language_result = (
            self.detector.from_analysis(
                analysis
            )
        )

        # ---------------------------------------------
        # 2. Decide response language policy
        # ---------------------------------------------

        policy = (
            self.policy_engine.decide(
                language_result
            )
        )

        # ---------------------------------------------
        # 3. Prepare language request
        # ---------------------------------------------

        processed_request = (
            self.processor.process(
                text=text,
                policy=policy
            )
        )

        return (
            language_result,
            policy,
            processed_request
        )

    # =================================================
    # FORMAT RESPONSE
    # =================================================

    def format_response(
        self,
        response: str,
        policy
    ):

        return self.formatter.format(
            response=response,
            policy=policy
        )