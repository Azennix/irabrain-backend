from sentence_transformers import SentenceTransformer


class EmbeddingService:
    _model = None

    def __init__(self):
        if EmbeddingService._model is None:
            print("Loading embedding model...")

            EmbeddingService._model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

        self.model = EmbeddingService._model

    def generate(self, text: str) -> list[float]:
        """Generate an embedding for one string."""
        return self.generate_batch([text])[0]

    def generate_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple strings."""
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embeddings.tolist()
