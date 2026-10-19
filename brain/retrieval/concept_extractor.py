from brain.embeddings.embedding_service import EmbeddingService

from brain.retrieval.concept import Concept
from brain.retrieval.concept_extraction_result import ConceptExtractionResult


class ConceptExtractor:

    def __init__(self, llm_service):

        self.llm = llm_service
        self.embedding_service = EmbeddingService()

    def extract(
        self,
        text: str
    ) -> ConceptExtractionResult:

        text = text.strip()

        if not text:
            return ConceptExtractionResult()

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

        for item in data.get("concepts", []):

            concept_text = str(
                item.get("text", "")
            ).strip()

            if not concept_text:
                continue

            confidence = float(
                item.get("confidence", 0.0)
            )

            embedding = (
                self.embedding_service.generate(
                    concept_text
                )
            )

            result.concepts.append(
                Concept(
                    text=concept_text,
                    embedding=embedding,
                    confidence=confidence
                )
            )

        return result