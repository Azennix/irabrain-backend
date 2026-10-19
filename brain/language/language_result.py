from dataclasses import dataclass


@dataclass(slots=True)
class LanguageResult:

    language: str

    confidence: float = 0.0

    is_mixed: bool = False

    secondary_language: str | None = None