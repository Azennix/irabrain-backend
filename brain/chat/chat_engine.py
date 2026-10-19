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