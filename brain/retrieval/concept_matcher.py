import numpy as np


class ConceptMatcher:

    def _similarity(
        self,
        a: list[float],
        b: list[float]
    ) -> float:

        a = np.array(a)
        b = np.array(b)

        denominator = (
            np.linalg.norm(a)
            * np.linalg.norm(b)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(a, b) / denominator
        )

    def match(
        self,
        concepts,
        memories
    ):

        best_matches = {}

        for concept in concepts.concepts:

            if not concept.embedding:
                continue

            for memory in memories:

                if not memory.embedding:
                    continue

                similarity = self._similarity(
                    concept.embedding,
                    memory.embedding
                )

                # -----------------------------
                # CONCEPT-AWARE SCORE
                # -----------------------------

                match_score = (
                    similarity
                    * concept.confidence
                )

                print(
                    f"CONCEPT MATCH | "
                    f"{concept.text} -> "
                    f"{memory.key} | "
                    f"similarity={similarity:.3f} | "
                    f"confidence={concept.confidence:.3f} | "
                    f"score={match_score:.3f}"
                )

                # Don't use a fixed 0.45 threshold here.
                # Keep only meaningful positive semantic matches.
                if match_score <= 0:
                    continue

                memory_id = memory.memory_id

                existing = best_matches.get(
                    memory_id
                )

                if (
                    existing is None
                    or match_score > existing[2]
                ):

                    best_matches[memory_id] = (
                        concept,
                        memory,
                        match_score
                    )

        return list(
            best_matches.values()
        )