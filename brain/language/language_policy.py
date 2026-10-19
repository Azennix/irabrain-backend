from dataclasses import dataclass

from brain.language.language_profile import LanguageProfile


@dataclass(slots=True)
class LanguagePolicy:

    # Language IRA should respond in
    response_language: str

    # Writing/script style of the user
    script: str = "latin"

    # Whether the user is mixing languages
    preserve_mixed_language: bool = False

    # Whether the user writes a language using another script
    preserve_transliteration: bool = False

    # User communication tone
    tone: str = "neutral"

    # How IRA should respond
    response_style: str = "standard"

    # Detection confidence
    confidence: float = 0.0


class LanguagePolicyEngine:

    """
    Converts LanguageProfile into LanguagePolicy.

    No LLM call.
    No translation.
    No response generation.
    """

    def decide(
        self,
        language_profile: LanguageProfile
    ) -> LanguagePolicy:

        # ==========================================
        # UNKNOWN / INVALID LANGUAGE
        # ==========================================

        if not language_profile.language:

            return LanguagePolicy(
                response_language="en",
                script="latin",
                preserve_mixed_language=False,
                preserve_transliteration=False,
                tone="neutral",
                response_style="standard",
                confidence=0.0
            )

        # ==========================================
        # NORMAL POLICY
        # ==========================================

        return LanguagePolicy(
            response_language=language_profile.language,
            script=language_profile.script or "latin",

            preserve_mixed_language=(
                language_profile.is_mixed
            ),

            preserve_transliteration=(
                language_profile.is_transliterated
            ),

            tone=(
                language_profile.tone
                or "neutral"
            ),

            response_style=(
                language_profile.response_style
                or "standard"
            ),

            confidence=max(
                0.0,
                min(
                    1.0,
                    language_profile.confidence
                )
            )
        )