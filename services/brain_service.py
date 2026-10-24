from sqlalchemy.orm import Session

from brain.base.brain_request import BrainRequest
from brain.orchestrator.brain_orchestrator import BrainOrchestrator
from brain.attachments.processor import AttachmentProcessor
from brain.self_development.integration.core_integration_service import (
    CoreIntegrationService,
)

class BrainService:

    def __init__(
        self,
        db: Session,
        core_integration_service: CoreIntegrationService | None = None,
    ):
        self.core_integration_service = (
            core_integration_service
            or CoreIntegrationService()
    )

        self.orchestrator = BrainOrchestrator(
            db=db,
            core_integration_service=self.core_integration_service,
        )
        self.attachment_processor = AttachmentProcessor()

    # =====================================================
    # CHAT
    # =====================================================

    def chat(
        self,
        user_id: int,
        query: str,
        conversation_id: str | None = None,
        project_id: str | None = None,
        user_name: str | None = None,
        attachments: list | None = None,
        workspace_mode: str = "personal",
        session_id: str | None = None,
    ) -> str:
        processed_attachments = [
        self.attachment_processor.process_attachment(
        attachment.model_dump()
    )
        for attachment in (attachments or [])
    ]

        request = BrainRequest(
            user_id=user_id,
            query=query,
            conversation_id=conversation_id,
            project_id=project_id,
            session_id=session_id,
            attachments=processed_attachments,
            metadata={
                 "user_name": user_name,
                 "workspace_mode": workspace_mode,
          },
        )

        return self.orchestrator.process(
            request=request
        )


    def chat_stream(
        self,
        user_id: int,
        query: str,
        conversation_id: str | None = None,
        project_id: str | None = None,
        user_name: str | None = None,
        attachments: list | None = None,
        workspace_mode: str = "personal",
        session_id: str | None = None,
        on_visual=None,
    ):
        processed_attachments = [
            self.attachment_processor.process_attachment(
                attachment.model_dump()
        )
            for attachment in (attachments or [])
    ]

        request = BrainRequest(
            user_id=user_id,
            query=query,
            conversation_id=conversation_id,
            project_id=project_id,
            session_id=session_id,
            attachments=processed_attachments,
            metadata={
               "user_name": user_name,
               "workspace_mode": workspace_mode,
        },
    )

        yield from self.orchestrator.process_stream(
            request=request,
            on_visual=on_visual,
        )

    def guest_chat(
        self,
        query: str,
        session_id: str,
    ) -> str:

        request = BrainRequest(
            user_id=0,
            query=query,
            session_id=session_id,
            metadata={
                "workspace_mode": "guest",
            },
        )

        return self.orchestrator.process(
            request=request
        )

        # =====================================================
    # CONVERSATION HISTORY
    # =====================================================

    def get_conversation_history(
        self,
        user_id: int,
        conversation_id: str | None = None,
        limit: int = 50
    ):


        return (
            self.orchestrator
            .conversation_service
            .get_conversation_history(
                user_id=user_id,
                conversation_id=conversation_id,
                limit=limit
            )
        )
        # =====================================================
    # CREATE CONVERSATION
    # =====================================================

    def create_conversation(
        self,
        user_id: int,
        conversation_id: str,
        title: str
    ):

        return (
            self.orchestrator
            .conversation_service
            .create_conversation(
                conversation_id=conversation_id,
                user_id=user_id,
                title=title
            )
        )

    # =====================================================
    # GET USER CONVERSATIONS
    # =====================================================

    def get_user_conversations(
        self,
        user_id: int,
        limit: int = 50
    ):

        return (
            self.orchestrator
            .conversation_service
            .get_user_conversations(
                user_id=user_id,
                limit=limit
            )
        )

    # =====================================================
    # GET CONVERSATION
    # =====================================================

    def get_conversation(
        self,
        user_id: int,
        conversation_id: str
    ):

        return (
            self.orchestrator
            .conversation_service
            .get_conversation(
                conversation_id=conversation_id,
                user_id=user_id
            )
        )

        # =====================================================
    # TOUCH CONVERSATION
    # =====================================================

    def touch_conversation(
        self,
        user_id: int,
        conversation_id: str
    ):

        return (
            self.orchestrator
            .conversation_service
            .touch_conversation(
                conversation_id=conversation_id,
                user_id=user_id
            )
        )

        # =====================================================
    # DELETE CONVERSATION
    # =====================================================

    def delete_conversation(
        self,
        user_id: int,
        conversation_id: str
    ) -> bool:

        return (
            self.orchestrator
            .conversation_service
            .delete_conversation(
                user_id=user_id,
                conversation_id=conversation_id
            )
        )

        # =====================================================
    # MEMORY
    # =====================================================

    def get_user_memories(
        self,
        user_id: int
    ):
        return self.orchestrator.memory_service.get_all_memories(
            user_id=user_id
        )
        # =====================================================
    # EDIT MEMORY
    # =====================================================

    def edit_memory(
        self,
        user_id: int,
        memory_id: str,
        category: str,
        key: str,
        value: str,
    ):
        return self.orchestrator.memory_service.edit_memory(
            user_id=user_id,
            memory_id=memory_id,
            category=category,
            key=key,
            value=value,
        )

    # =====================================================
    # FORGET MEMORY
    # =====================================================

    def forget_memory(
        self,
        user_id: int,
        memory_id: str,
    ) -> bool:
        return self.orchestrator.memory_service.forget_memory(
            user_id=user_id,
            memory_id=memory_id,
        )

    def commit(self):
        self.orchestrator.conversation_service.commit()


    # =====================================================
    # CLOSE
    # =====================================================

    def close(self) -> None:

        self.orchestrator.close()