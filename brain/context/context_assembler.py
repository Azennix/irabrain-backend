from brain.context.context_builder import ContextBuilder
from brain.conversation.conversation_service import ConversationService
from brain.context.context_model import Context
from brain.conversation.conversation_service import ConversationService

class ContextAssembler:
    """
    Assembles the complete context used by IRABrain.

    Responsibilities:

    1. Build long-term memory context
    2. Retrieve recent conversation history
    3. Combine memory and conversation into Context

    It does NOT:

    - retrieve memories directly
    - score memories
    - select memories
    - compress memories
    - manage conversations directly
    - perform reasoning
    - generate responses
    """

    def __init__(
        self,
        context_builder: ContextBuilder,
        conversation_service: ConversationService,
        conversation_summary_service
    ):
        self.context_builder = context_builder
        self.conversation_service = conversation_service
        self.conversation_summary_service = (
            conversation_summary_service
    )
    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    def build(
        self,
        user_id: int,
        user_message: str,
        memories=None,
        conversation_limit: int = 10,
        include_memory: bool = True,
        current_message_id: int | None = None,
        conversation_id: str | None = None
    ) -> Context:

        # =================================================
        # 1. LONG-TERM MEMORY
        # =================================================

        memory_context = self.context_builder.build(
            user_id=user_id,
            user_message=user_message,
            memories=memories,
            include_memory=include_memory,

        )

        # =================================================
        # 2. CONVERSATION HISTORY
        # =================================================

        conversation_history = (
            self.conversation_service.get_recent_conversation(
                user_id=user_id,
                current_message_id=current_message_id,
                current_message=user_message,
                limit=conversation_limit,
                conversation_id=conversation_id
            )
        )



        # =================================================
        # 3. CONVERSATION SUMMARY
        # =================================================

        conversation_summary = None

        if conversation_id is not None:
            summary_model = (
                self.conversation_summary_service.get_summary(
                    conversation_id=conversation_id,
                    user_id=user_id,
                )
            )

            if summary_model is not None:
                conversation_summary = summary_model.summary

        # =================================================
        # 4. UNIFIED CONTEXT
        # =================================================

        return Context(
            memory=memory_context,
            conversation=conversation_history,
            conversation_summary=conversation_summary,
        )