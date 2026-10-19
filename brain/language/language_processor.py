from dataclasses import dataclass

from brain.language.language_policy import LanguagePolicy


@dataclass(slots=True)
class LanguageProcessedRequest:

    text: str

    response_language: str

    preserve_mixed_language: bool = False


class LanguageProcessor:

    """
    Prepares a request according to the selected
    language policy.

    It does not:
    - detect language
    - select policy
    - generate response
    - translate response

    It only prepares language information
    for the downstream Brain pipeline.
    """

    def process(
        self,
        text: str,
        policy: LanguagePolicy
    ) -> LanguageProcessedRequest:

        return LanguageProcessedRequest(
            text=text.strip(),
            response_language=policy.response_language,
            preserve_mixed_language=(
            policy.preserve_mixed_language
            )
        )