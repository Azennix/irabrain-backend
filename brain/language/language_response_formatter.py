from dataclasses import dataclass

from brain.language.language_policy import LanguagePolicy


@dataclass(slots=True)
class FormattedResponse:

    content: str

    language: str

    was_transformed: bool = False


class LanguageResponseFormatter:

    """
    Final response formatting boundary for IRABrain.

    The core Chat LLM is responsible for generating
    the response in the requested language and style.

    This formatter does NOT:

    - detect language
    - select language policy
    - generate responses
    - translate responses
    - rewrite responses

    V1 simply preserves the generated response and
    attaches the language metadata.
    """

    def format(
        self,
        response: str,
        policy: LanguagePolicy
    ) -> FormattedResponse:

        content = (
            response.strip()
            if response
            else ""
        )

        return FormattedResponse(
            content=content,
            language=policy.response_language,
            was_transformed=False
        )