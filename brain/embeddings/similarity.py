import numpy as np


class SimilarityService:

    @staticmethod
    def cosine_similarity(a, b):
        a = np.asarray(a, dtype=np.float32)
        b = np.asarray(b, dtype=np.float32)

        if a.shape != b.shape:
            raise ValueError("Embedding dimensions must match.")

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        denominator = norm_a * norm_b
        if denominator == 0:
            return 0.0

        return float(np.dot(a, b) / denominator)
