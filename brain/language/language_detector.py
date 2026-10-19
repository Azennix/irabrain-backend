from brain.language.language_profile import LanguageProfile
from brain.memory.message_analysis_result import MessageAnalysisResult


class LanguageDetector:
    """
    Converts the language information produced by
    MessageAnalyzer into a LanguageProfile.

    IMPORTANT:

    This class DOES NOT call the LLM.

    MessageAnalyzer is responsible for language judgment.
    LanguageDetector only creates the application's
    LanguageProfile object from that result.
    """


    # =====================================================
    # CREATE LANGUAGE PROFILE
    # =====================================================

    def from_analysis(
        self,
        analysis: MessageAnalysisResult
    ) -> LanguageProfile:

        language = self._normalize_language(
         analysis.language
)

        script = self._normalize_script(
         analysis.script
)

        is_mixed = analysis.is_mixed

        secondary_language = analysis.secondary_language

        is_transliterated = analysis.is_transliterated

        tone = self._normalize_tone(
        analysis.tone
)

        response_style = self._normalize_response_style(
        analysis.response_style
)

        confidence = self._safe_float(
          analysis.confidence
)

        return LanguageProfile(
            language=language,

            script=script,

            is_mixed=is_mixed,

            secondary_language=secondary_language,

            is_transliterated=is_transliterated,

            tone=tone,

            response_style=response_style,

            confidence=confidence
        )

    # =====================================================
    # LANGUAGE NORMALIZATION
    # =====================================================

    @staticmethod
    def _normalize_language(
        value
    ) -> str:

        value = str(
            value or "en"
        ).strip().lower()

        allowed = {
            "en",
            "te",
            "hi",
            "ta",
            "kn",
            "ml",
            "other"
        }

        if value not in allowed:
            return "other"

        return value

    # =====================================================
    # SCRIPT NORMALIZATION
    # =====================================================

    @staticmethod
    def _normalize_script(
        value
    ) -> str:

        value = str(
            value or "latin"
        ).strip().lower()

        allowed = {
            "latin",
            "telugu",
            "devanagari",
            "tamil",
            "kannada",
            "malayalam",
            "other"
        }

        if value not in allowed:
            return "other"

        return value

    # =====================================================
    # TONE NORMALIZATION
    # =====================================================

    @staticmethod
    def _normalize_tone(
        value
    ) -> str:

        value = str(
            value or "neutral"
        ).strip().lower()

        allowed = {
            "casual",
            "neutral",
            "formal",
            "professional"
        }

        if value not in allowed:
            return "neutral"

        return value

    # =====================================================
    # RESPONSE STYLE
    # =====================================================

    @staticmethod
    def _normalize_response_style(
        value
    ) -> str:

        value = str(
            value or "standard"
        ).strip().lower()
        allowed = {
            "casual_tenglish",
            "telugu",
            "casual_english",
            "casual_mixed",
            "formal_telugu",
            "professional_english",
            "standard"
        }

        if  value not in allowed:
            return "standard"

        return value

    # =====================================================
    # FLOAT SAFETY
    # =====================================================

    @staticmethod
    def _safe_float(
        value
    ) -> float:

        try:
            value = float(value)

        except (
            TypeError,
            ValueError
        ):
            return 0.7

        return max(
            0.0,
            min(
                1.0,
                value
            )
        )
