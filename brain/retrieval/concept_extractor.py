from collections import OrderedDict
from threading import RLock

from brain.embeddings.embedding_service import EmbeddingService

from brain.retrieval.concept import Concept
from brain.retrieval.concept_extraction_result import ConceptExtractionResult


class ConceptExtractor:

    CONCEPT_CACHE_MAX_SIZE = 128

    def __init__(self, llm_service):
        self.llm = llm_service
        self.embedding_service = EmbeddingService()
        self._concept_cache = OrderedDict()
        self._cache_lock = RLock()

    @staticmethod
    def _copy_result(result: ConceptExtractionResult) -> ConceptExtractionResult:
        return ConceptExtractionResult(
            concepts=[
                Concept(
                    text=concept.text,
                    embedding=(
                        list(concept.embedding)
                        if concept.embedding is not None
                        else None
                    ),
                    confidence=concept.confidence,
                )
                for concept in result.concepts
            ],
            confidence=result.confidence,
            reasoning=result.reasoning,
        )

    def extract(
        self,
        text: str
    ) -> ConceptExtractionResult:

        text = text.strip()

        if not text:
            return ConceptExtractionResult()

        cache_key = text

        with self._cache_lock:
            cached_result = self._concept_cache.get(cache_key)
            if cached_result is not None:
                self._concept_cache.move_to_end(cache_key)
                return self._copy_result(cached_result)

        prompt = f"""
You are the concept extraction engine for IRABRAIN.

Extract the important semantic concepts from the user's message.

The concepts should represent meaningful topics, entities, skills,
projects, goals, technologies, interests, or other useful semantic ideas.

Do NOT simply return every word.

USER MESSAGE:
<user_message>
{text}
</user_message>

Return ONLY valid JSON:

{{
    "concepts": [
        {{
            "text": "concept",
            "confidence": 0.0
        }}
    ],
    "confidence": 0.0,
    "reasoning": "short explanation"
}}

Confidence must be between 0.0 and 1.0.

Return an empty concepts array if there are no meaningful concepts.
"""

        data = self.llm.generate_structured(
            prompt=prompt,
            temperature=0.0
        )

        result = ConceptExtractionResult()

        result.confidence = float(
            data.get("confidence", 0.0)
        )

        result.reasoning = data.get(
            "reasoning",
            ""
        )

        valid_concepts = []

        for item in data.get("concepts", []):
            if not isinstance(item, dict):
                continue

            concept_text = str(item.get("text", "")).strip()
            if not concept_text:
                continue

            try:
                confidence = float(item.get("confidence", 0.0))
            except (TypeError, ValueError):
                confidence = 0.0

            valid_concepts.append((concept_text, confidence))

        embeddings = self.embedding_service.generate_batch(
            [text for text, _ in valid_concepts]
        )

        for (concept_text, confidence), embedding in zip(
            valid_concepts,
            embeddings,
        ):
            result.concepts.append(
                Concept(
                    text=concept_text,
                    embedding=embedding,
                    confidence=confidence
                )
            )

        with self._cache_lock:
            self._concept_cache[cache_key] = self._copy_result(result)
            self._concept_cache.move_to_end(cache_key)

            while len(self._concept_cache) > self.CONCEPT_CACHE_MAX_SIZE:
                self._concept_cache.popitem(last=False)

        return result
