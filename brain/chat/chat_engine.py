from brain.engine.engine import Engine
from brain.llm.chat_prompt_builder import ChatPromptBuilder
from brain.chat.response_validator import ResponseValidator
from brain.chat.confidence_controller import ConfidenceController
from brain.llm.llm_request_context import LLMRequestContext

class ChatEngine(Engine):

    def __init__(
        self,
        llm_service
    ):
        self.llm_service = llm_service

        self.response_validator = (
            ResponseValidator()
        )

        self.confidence_controller = (
            ConfidenceController()
        )

    # =====================================================
    # NORMAL RESPONSE
    # Existing pipeline
    # =====================================================

    def execute(
        self,
        request,
        context,
        conversation_history=None,
        reasoning_result=None,
        tool_result=None,
        language_policy=None
    ):

        prompt = ChatPromptBuilder.build(
            user_message=request.query,
            context=context,
            conversation_history=conversation_history,
            reasoning_result=reasoning_result,
            tool_result=tool_result,
            language_policy=language_policy,
            attachments=request.attachments,
            workspace_mode=request.metadata.get(
               "workspace_mode",
               "personal",
    ),
)

        llm_response = self.llm_service.generate(
             prompt
)

        response = llm_response.content

        response = (
            self.response_validator.validate(
                response
            )
        )

        confidence = 1.0

        if reasoning_result is not None:
            confidence = (
                reasoning_result.confidence
            )

        response = (
            self.confidence_controller.adjust(
                response=response,
                confidence=confidence
            )
        )

        print(
            "\n========== IRABRAIN =========="
        )

        print(response)

        print(
            "=============================="
        )

        return response

    # =====================================================
    # STREAMING RESPONSE
    # Final IRA answer only
    # =====================================================

    def execute_stream(
        self,
        request,
        context,
        conversation_history=None,
        reasoning_result=None,
        tool_result=None,
        language_policy=None,
        brain_tier=None,
    ):

        prompt = ChatPromptBuilder.build(
            user_message=request.query,
            context=context,
            conversation_history=conversation_history,
            reasoning_result=reasoning_result,
            tool_result=tool_result,
            language_policy=language_policy,
            attachments=request.attachments,
            workspace_mode=request.metadata.get(
             "workspace_mode",
             "personal"
),
        )

        request_context = LLMRequestContext(
            request_id=request.request_id,
            user_id=request.user_id,
            brain_tier=brain_tier,
        )

        # Keep complete response locally.
        full_response = ""



        # Stream chunks from the configured LLM provider.
        for chunk in self.llm_service.generate_stream(
            prompt,
            request_context=request_context,
        ):



            full_response += chunk

            # Send chunk to caller immediately.
            yield chunk

        # Validate complete response after streaming.
        validated_response = (
            self.response_validator.validate(
                full_response
            )
        )

        confidence = 1.0

        if reasoning_result is not None:
            confidence = (
                reasoning_result.confidence
            )

        final_response = (
            self.confidence_controller.adjust(
                response=validated_response,
                confidence=confidence
            )
        )

        print(
            "\n========== IRABRAIN STREAM COMPLETE =========="
        )

        print(final_response)

        print(
            "=============================================="
        )
    def generate_visual(
        self,
        *,
        user_message: str,
        assistant_response: str,
        request_context: LLMRequestContext,
    ) -> dict | None:

        prompt = f"""
Create a visual representation only Create a simple, clear, structured visual that helps the user understand the answer.

USER QUESTION:
{user_message}

ASSISTANT ANSWER:
{assistant_response}

Choose the most suitable visual type:

* concept_map: connected concepts and their relationships.
* flowchart: a process or sequence of actions.
* comparison: differences or similarities between two or more things.
* steps: an ordered explanation or procedure.

Return a valid JSON object with these fields:

* type: concept_map, flowchart, comparison, steps, or none
* title: short descriptive title
* description: optional, concise explanation
* nodes: concept map nodes with id, label, and optional description
* edges: connections with from, to, and optional label
* steps: ordered items with title and optional description
* columns: comparison column names
* comparisons: comparison items with label and values

Visual design rules:

* Prefer the simplest visual that makes the answer easier to understand.
* Use short labels and concise descriptions.
* Keep each box focused on one idea.
* Use clear relationships and meaningful connections.
* For concept maps, create a central concept and its main related concepts. Use edges to connect them.
* For flowcharts, show the process in the correct order.
* For steps, show a clear numbered sequence.
* For comparisons, use aligned columns with matching comparison categories.
* Include only the fields needed for the selected visual type.
* Use only facts supported by the assistant's answer.
* Do not repeat the full text answer inside the visual.
* Never generate ASCII diagrams, text-drawn boxes, Markdown tables, or code fences.
* Do not put multiple unrelated ideas into one box.
* Avoid unnecessarily large or complicated visuals.
* If a visual genuinely adds no value, return {{"type": "none"}}.

Return valid JSON only. Do not include Markdown fences.
"""

        try:
            visual = self.llm_service.generate_structured(
                prompt,
                temperature=0.0,
            )

            if not isinstance(visual, dict):
                return None

            visual_type = visual.get("type")

            if visual_type == "none":
                return None

            if visual_type not in {
                "concept_map",
                "flowchart",
                "comparison",
                "steps",
            }:
                return None

            if not isinstance(visual.get("title"), str):
                return None

            visual["title"] = visual["title"][:200]

            return visual

        except Exception as error:
            print(
                "[VISUAL INTELLIGENCE] Generation failed:",
                str(error),
            )
            return None
