from dataclasses import dataclass


@dataclass(frozen=True)
class RankingConfig:

    keyword_weight: float = 0.20
    semantic_weight: float = 0.45
    association_weight: float = 0.15
    concept_weight: float = 0.20