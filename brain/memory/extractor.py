import uuid

from brain.base.brain_request import BrainRequest
from brain.llm.llm_service import LLMService
from brain.llm.prompt_builder import PromptBuilder
from brain.memory.memory_extraction_result import MemoryExtractionResult
from brain.memory.memory_model import Memory


class MemoryExtractor:

    def __init__(
        self,
        llm_service: LLMService
    ):
        self.llm = llm_service

    def extract(
        self,
        request: BrainRequest
    ) -> MemoryExtractionResult:

        prompt = PromptBuilder.memory_extraction(
            request.query
        )

        try:
            data = self.llm.generate_structured(
                prompt=prompt,
                temperature=0.0
            )
        except Exception as e:
            print("\n=========⚠ Invalid JSON========")
            print(e)
            print("Retrying..once...\n")
            print("===============================\n")

            try:

              data = self.llm.generate_structured(
                prompt=prompt,
                temperature=0.0
            )

            except Exception as e:
                print("\n========== RETRY FAILED ==========")
                print(e)
                print("Skipping memory extraction.")
                print("=================================\n")


            return MemoryExtractionResult(
                memories=[],
                reasoning="JSON Parsing Failed",
                confidence=0.0

         )







        return self._parse_result(
            request=request,
            data=data
        )

    def _parse_result(
        self,
        request: BrainRequest,
        data: dict
    ) -> MemoryExtractionResult:

        memories = []

        for item in data.get("memories", []):

            category = item["category"]

            memory = Memory(

                memory_id=str(uuid.uuid4()),

                user_id=request.user_id,

                category=category,

                key=item["key"],

                value=item["value"],

                confidence=item["confidence"]

            )

            memories.append(memory)

        return MemoryExtractionResult(

            memories=memories,

            reasoning=data.get(
                "reasoning",
                ""
            ),

            confidence=data.get(
                "confidence",
                0.0
            )

        )