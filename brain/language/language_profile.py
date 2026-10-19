from dataclasses import dataclass
from typing import Optional


@dataclass
class LanguageProfile:

    language: str
    script: str
    is_mixed: bool
    secondary_language: Optional[str] = None
    is_transliterated: bool = False
    tone: str = "neutral"
    response_style: str = "standard"
    confidence: float = 0.0