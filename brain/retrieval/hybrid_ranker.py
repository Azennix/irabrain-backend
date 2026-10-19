from brain.retrieval.ranking_config import RankingConfig


class HybridRanker:

    def __init__(
        self,
        config: RankingConfig
    ):
        self.config = config

    def rank(self, results):

        for result in results:

            result.final_score = (
                result.keyword_score * self.config.keyword_weight
                + result.semantic_score * self.config.semantic_weight
                + result.association_score * self.config.association_weight
                + result.concept_score * self.config.concept_weight
            )

        return sorted(
            results,
            key=lambda result: result.final_score,
            reverse=True
        )