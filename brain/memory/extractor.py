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

    def extract(self, request: BrainRequest) -> MemoryExtractionResult:
        prompt = PromptBuilder.memory_extraction(request.query)

        try:
            data = self.llm.generate_structured(
                prompt=prompt,
                temperature=0.0,
            )
        except Exception as first_error:
            print("\n========= MEMORY EXTRACTION RETRY =========")
            print(first_error)
            print("Retrying once...")
            print("===========================================\n")

            try:
                data = self.llm.generate_structured(
                    prompt=prompt,
                    temperature=0.0,
                )
            except Exception as retry_error:
                print("\n========= MEMORY EXTRACTION FAILED =========")
                print(retry_error)
                print("Skipping memory extraction.")
                print("=============================================\n")

                return MemoryExtractionResult(
                    memories=[],
                    reasoning="Memory extraction failed after retry",
                    confidence=0.0,
                )

        return self._parse_result(request=request, data=data)

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