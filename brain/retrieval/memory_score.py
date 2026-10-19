from math import log1p



class MemoryScore:

    def score(
        self,
        importance: float,
        confidence: float,
        access: int,
        recency: float
    ) -> float:

        access_score = min(
            log1p(access) / log1p(10),
            1.0
        )

        score = (
            importance * 0.40
            + confidence * 0.30
            + access_score * 0.15
            + recency * 0.15
        )

        return min(
            max(score, 0.0),
            1.0
        )