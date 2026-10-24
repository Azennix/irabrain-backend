from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
import json
from services.brain_service import BrainService
from security.dependencies import get_current_user

from api.schemas.brain_schema import (
    BrainChatRequest,
    CreateConversationRequest,
    ConversationSummaryResponse,
    UpdateMemoryRequest,
    BrainBalanceResponse,
    )
from brain.conversation.conversation_title_service import (
    generate_conversation_title,
)
from api.dependencies import (
    get_brain_service,
    get_brain_balance_service,
)
from brain.recharge.balance_service import BrainBalanceService
from brain.tier.entitlement.errors import TierEntitlementError
from brain.tier.capability_policy import CapabilityPolicy
from brain.tier.capability_requirement import CapabilityRequirement
from brain.tier.entitlement.service import TierEntitlementService
from brain.tier.models import BrainTier

router = APIRouter(
    prefix="/brain",
    tags=["Brain"]
)

def _entitlement_error_response(error: TierEntitlementError) -> dict:
    detail = {
        "code": error.code,
        "message": (
            "This task requires a capability that isn't included "
            "in your current Brain tier."
            if error.code == "CAPABILITY_NOT_INCLUDED"
            else "This task exceeds the context capacity of your current Brain tier."
            if error.code == "CONTEXT_LIMIT_EXCEEDED"
            else "This task requires more reasoning capability than your current Brain tier supports."
            if error.code == "COMPLEXITY_LIMIT_EXCEEDED"
            else "This task cannot be completed with your current Brain tier."
        ),
        "required_tier": error.required_tier,
    }

    return {"detail": detail}
# =====================================================
# CONVERSATIONS
# =====================================================

@router.post(
    "/conversations",
    response_model=ConversationSummaryResponse
)
def create_conversation(
    request: CreateConversationRequest,
    current_user=Depends(get_current_user),
    brain_service: BrainService = Depends(get_brain_service)
):
    import uuid

    conversation = brain_service.create_conversation(
        user_id=current_user.user_id,
        conversation_id=str(uuid.uuid4()),
        title=request.title
    )

    brain_service.commit()

    return conversation


@router.get(
    "/conversations",
    response_model=list[ConversationSummaryResponse]
)
def get_conversations(
    current_user=Depends(get_current_user),
    brain_service: BrainService = Depends(get_brain_service)
):
    return brain_service.get_user_conversations(
        user_id=current_user.user_id
    )


# =====================================================
# BRAIN BALANCE
# =====================================================

@router.get(
    "/balance",
    response_model=BrainBalanceResponse,
)

def get_brain_balance(
    current_user=Depends(get_current_user),
    balance_service: BrainBalanceService = Depends(
        get_brain_balance_service
    ),
):
    return balance_service.get_balance(
        user_id=current_user.user_id
    )




# =====================================================
# DELETE CONVERSATION
# =====================================================

@router.delete(
    "/conversations/{conversation_id}"
)
def delete_conversation(
    conversation_id: str,
    current_user=Depends(get_current_user),
    brain_service: BrainService = Depends(
        get_brain_service
    )
):
    deleted = brain_service.delete_conversation(
        user_id=current_user.user_id,
        conversation_id=conversation_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    brain_service.commit()

    return {
        "success": True
    }

@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationSummaryResponse
)

def get_conversation(
    conversation_id: str,
    current_user=Depends(get_current_user),
    brain_service: BrainService = Depends(get_brain_service)
):


    conversation = brain_service.get_conversation(
        user_id=current_user.user_id,
        conversation_id=conversation_id
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Mark conversation as recently opened
    brain_service.touch_conversation(
        user_id=current_user.user_id,
        conversation_id=conversation_id
    )

    brain_service.commit()

    return conversation




# =====================================================
# CHAT
# =====================================================

@router.post("/chat")
def chat(
    request: BrainChatRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    brain_service: BrainService = Depends(
        get_brain_service
    )
):
    try:

        response = brain_service.chat(
            user_id=current_user.user_id,
            query=request.query,
            conversation_id=request.conversation_id,
            project_id=request.project_id,
            user_name=current_user.full_name,
            attachments=request.attachments,
            workspace_mode=request.workspace_mode,
            session_id=request.session_id,
    )


    except TierEntitlementError as error:
        status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=_entitlement_error_response(error)["detail"],
        ) from error
    # Generate the smart conversation title in the background.
    # This does NOT block the chat response.
    if request.conversation_id:
        background_tasks.add_task(
            generate_conversation_title,
            user_id=current_user.user_id,
            conversation_id=request.conversation_id,
            user_message=request.query,
            assistant_response=response,
            llm_service=brain_service.orchestrator.llm_service,
        )

    return {
        "response": response
    }


# =====================================================
# CONVERSATION HISTORY
# =====================================================

@router.get("/conversation")
def get_conversation_history(
    conversation_id: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    brain_service: BrainService = Depends(
        get_brain_service
    )
):

    messages = (
        brain_service
        .get_conversation_history(
            user_id=current_user.user_id,
            conversation_id=conversation_id
        )
    )

    return {
        "messages": [
            {
                "id": message.message_id,
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]
    }



# =====================================================
# MEMORY
# =====================================================

@router.get("/memories")
def get_memories(
    current_user=Depends(get_current_user),
    brain_service: BrainService = Depends(
        get_brain_service
    )
):
    memories = brain_service.get_user_memories(
        user_id=current_user.user_id
    )

    return {
        "memories": [
            {
                "id": memory.memory_id,
                "category": memory.category,
                "key": memory.key,
                "value": memory.value,
                "confidence": memory.confidence,
            }
            for memory in memories
        ]
    }
# =====================================================
# EDIT MEMORY
# =====================================================

@router.patch("/memories/{memory_id}")
def edit_memory(
    memory_id: str,
    request: UpdateMemoryRequest,
    current_user=Depends(get_current_user),
    brain_service: BrainService = Depends(
        get_brain_service
    )
):
    try:
        memory = brain_service.edit_memory(
            user_id=current_user.user_id,
            memory_id=memory_id,
            category=request.category,
            key=request.key,
            value=request.value,
        )

    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Memory not found"
        )

    return {
        "memory": {
            "id": memory.memory_id,
            "category": memory.category,
            "key": memory.key,
            "value": memory.value,
            "confidence": memory.confidence,
        }
    }


# =====================================================
# FORGET MEMORY
# =====================================================

@router.delete("/memories/{memory_id}")
def forget_memory(
    memory_id: str,
    current_user=Depends(get_current_user),
    brain_service: BrainService = Depends(
        get_brain_service
    )
):
    deleted = brain_service.forget_memory(
        user_id=current_user.user_id,
        memory_id=memory_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Memory not found"
        )

    return {
        "success": True
    }


# =====================================================
# STREAMING CHAT
# =====================================================

@router.post("/chat/stream")
def chat_stream(
    request: BrainChatRequest,
    current_user=Depends(get_current_user),
    brain_service: BrainService = Depends(get_brain_service),
):
    visual_payloads = []
    try:
        stream = brain_service.chat_stream(
            user_id=current_user.user_id,
            query=request.query,
            conversation_id=request.conversation_id,
            project_id=request.project_id,
            user_name=current_user.full_name,
            attachments=request.attachments,
            workspace_mode=request.workspace_mode,
            session_id=request.session_id,
            on_visual=visual_payloads.append
        )
    except TierEntitlementError as error:
        raise HTTPException(
            status_code=403,
            detail=_entitlement_error_response(error)["detail"],
        ) from error

    try:
        first_chunk = next(stream)
    except StopIteration:
        first_chunk = None
    except TierEntitlementError as error:
        stream.close()
        raise HTTPException(
            status_code=403,
            detail=_entitlement_error_response(error)["detail"],
        ) from error
    except Exception as error:
        stream.close()
        raise HTTPException(
            status_code=500,
            detail="I'm having trouble processing your request right now. Please try again shortly.",
        ) from error

    def generate():
        assistant_chunks = []

        try:
            if first_chunk is not None:
                assistant_chunks.append(first_chunk)

                yield (
                    "event: chunk\n"
                    f"data: {json.dumps({'text': first_chunk})}\n\n"
            )

            for chunk in stream:
                assistant_chunks.append(chunk)

                yield (
                    "event: chunk\n"
                    f"data: {json.dumps({'text': chunk})}\n\n"
            )

        # Generate a title only after the response completes.
        # Reuse the existing title-generation service.
            if (
                request.conversation_id
                and request.workspace_mode == "personal"
                and assistant_chunks
        ):
                try:
                    generate_conversation_title(
                        user_id=current_user.user_id,
                        conversation_id=request.conversation_id,
                       user_message=request.query,
                       assistant_response="".join(assistant_chunks),
                       llm_service=brain_service.orchestrator.llm_service,
                )
                except Exception:
                # Title generation must not break a successful chat.
                    pass
            for visual_payload in visual_payloads:
                print(
                    "[VISUAL DEBUG] Sending visual event:",
                    visual_payload.get("type"),
                )
                yield (
                    "event: visual\n"
                    f"data: {json.dumps({'visual': visual_payload})}\n\n"
                )

            yield (
                "event: complete\n"
                'data: {"success": true}\n\n'
        )

        except Exception:
            yield (
                "event: error\n"
                + 'data: {"message": "The response was interrupted before it finished. Please try again."}\n\n'
        )

        finally:
            stream.close()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )