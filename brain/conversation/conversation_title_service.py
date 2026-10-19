from database.database import SessionLocal

from brain.conversation.conversation_service import ConversationService
from brain.conversation.conversation_scorer import ConversationScorer
from brain.conversation.conversation_title_generator import (
    ConversationTitleGenerator,
)
from brain.llm.memory_llm_service import MemoryLLMService


def generate_conversation_title(
    user_id: int,
    conversation_id: str,
    user_message: str,
    assistant_response: str,
    llm_service,
) -> None:
    """
    Generate and persist a smart conversation title.

    This function creates its own database session because it
    runs as a background task after the chat response is returned.
    """

    db = SessionLocal()

    try:


        conversation_scorer = ConversationScorer(
            llm_service=llm_service
        )

        conversation_service = ConversationService(
            db=db,
            scorer=conversation_scorer,
        )

        conversation = (
            conversation_service.get_conversation(
                conversation_id=conversation_id,
                user_id=user_id,
            )
        )

        if conversation is None:
            print(
                "[WARNING] Conversation not found for title generation"
            )
            return


                # -------------------------------------------------
        # GENERATE TITLE ONLY ONCE
        # -------------------------------------------------

        if conversation.title != "New Conversation":
            print(
                "[INFO] Conversation already has a title. "
                "Skipping title generation."
            )
            return

        title_generator = ConversationTitleGenerator(
            llm_service=llm_service
        )

        title = title_generator.generate(
            user_message=user_message,
            assistant_response=assistant_response,
        )

        conversation_service.update_conversation(
            conversation=conversation,
            title=title,
        )

        conversation_service.commit()

        print("[OK] Conversation title generated")
        print("Title :", title)


    except Exception as error:
        print(
            "[WARNING] Conversation title generation failed:",
            error,
        )

        db.rollback()

    finally:
        db.close()