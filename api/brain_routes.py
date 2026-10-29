from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
import json
from services.brain_service import BrainService
from security.dependencies import get_current_user
import time
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
from database.database import SessionLocal
from brain.self_development.integration.core_integration_service import (
    CoreIntegrationService,
)
from brain.self_development.integration.self_development_factory import (
    create_self_development_gateway,
)

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

# Global executor - FastAPI ni block cheyaku
stream_executor = ThreadPoolExecutor(max_workers=20, thread_name_prefix="brain_parallel")


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
                "visual_data": getattr(message, "visual_data", None),
                "attachments": getattr(message, "attachments", None) or [],
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

# =====================================================
# STREAMING CHAT - REAL PIPELINE STATES
# =====================================================

@router.post("/chat/stream")
async def chat_stream(
    request: BrainChatRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    brain_service: BrainService = Depends(get_brain_service),
):
    event_queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    stream_started_at = time.perf_counter()
    first_chunk_logged = False
    # Capture plain values before entering the worker thread.
    stream_user_id = current_user.user_id
    stream_user_name = current_user.full_name

    def on_visual_callback(payload):
        try:
            loop.call_soon_threadsafe(event_queue.put_nowait, {"type": "visual", "payload": payload})
        except Exception as e:
            print(f"[VISUAL CALLBACK ERROR] {e}")

    def on_state_callback(state): # <-- REAL STATES
        try:
            print(f"[REAL STATE QUEUE] {state}")
            loop.call_soon_threadsafe(event_queue.put_nowait, {"type": "state", "payload": state})
        except Exception as e:
            print(f"[STATE CALLBACK ERROR] {e}")

    def run_brain_sync():
        worker_db = SessionLocal()
        worker_service = None

        try:
            # Build the integration inside the worker.
            self_development_gateway = create_self_development_gateway()
            core_integration_service = CoreIntegrationService(
                signal_handler=self_development_gateway.process,
            )

            # The worker owns its own SQLAlchemy session.
            worker_service = BrainService(
                db=worker_db,
                core_integration_service=core_integration_service,
            )

            stream = worker_service.chat_stream(
                user_id=stream_user_id,
                query=request.query,
                conversation_id=request.conversation_id,
                project_id=request.project_id,
                user_name=stream_user_name,
                attachments=request.attachments,
                workspace_mode=request.workspace_mode,
                session_id=request.session_id,
                on_visual=on_visual_callback,
                on_state=on_state_callback,
            )

            for chunk in stream:
                loop.call_soon_threadsafe(
                    event_queue.put_nowait,
                    {"type": "chunk", "payload": chunk},
                )

            loop.call_soon_threadsafe(
                event_queue.put_nowait,
                {"type": "text_complete"},
            )
            loop.call_soon_threadsafe(
                event_queue.put_nowait,
                {"type": "complete"},
            )

        except Exception as exc:
            import traceback

            print(f"[BRAIN THREAD ERROR] {exc}")
            traceback.print_exc()
            loop.call_soon_threadsafe(
                event_queue.put_nowait,
                {"type": "error", "payload": str(exc)},
            )

        finally:
            try:
                if worker_service is not None:
                    worker_service.close()
            except Exception as exc:
                print(f"[BRAIN SERVICE CLOSE ERROR] {exc}")
            finally:
                worker_db.close()

    executor_future = loop.run_in_executor(stream_executor, run_brain_sync)

    async def event_generator():
        nonlocal first_chunk_logged

        full_text = []

        try:
            while True:
                event = await event_queue.get()
                event_type = event["type"]

                if event_type == "chunk":
                    if not first_chunk_logged:
                        first_chunk_logged = True
                        print(
                            "[SSE TIMING] First chunk reached event_generator: "
                            f"{time.perf_counter() - stream_started_at:.3f}s"
                    )

                    full_text.append(event["payload"])

                    yield (
                        "event: chunk\n"
                        f"data: {json.dumps({'text': event['payload']})}\n\n"
                )

                elif event_type == "visual":
                    try:
                        visual_json = json.dumps({
                            "visual": event["payload"]
                        })

                        yield (
                            "event: visual\n"
                            f"data: {visual_json}\n\n"
                    )

                    except (TypeError, ValueError) as exc:
                        print(
                            "[SSE VISUAL SERIALIZATION ERROR] "
                            f"{type(exc).__name__}: {exc}"
                    )

                elif event_type == "state":
                    try:
                        state_json = json.dumps({
                            "state": event["payload"]
                        })

                        yield (
                            "event: state\n"
                            f"data: {state_json}\n\n"
                    )

                    except (TypeError, ValueError) as exc:
                        print(
                            "[SSE STATE SERIALIZATION ERROR] "
                            f"{type(exc).__name__}: {exc}"
                    )

                elif event_type == "text_complete":
                    yield (
                        "event: text_complete\n"
                        'data: {"success": true}\n\n'
                )

                    if (
                        request.conversation_id
                        and request.workspace_mode == "personal"
                        and full_text
                ):
                        background_tasks.add_task(
                            generate_conversation_title,
                            user_id=current_user.user_id,
                            conversation_id=request.conversation_id,
                            user_message=request.query,
                            assistant_response="".join(full_text),
                            llm_service=brain_service.orchestrator.llm_service,
                    )

                elif event_type == "complete":
                    yield (
                        "event: complete\n"
                        'data: {"success": true}\n\n'
                )
                    break

                elif event_type == "error":
                    yield (
                        "event: error\n"
                        f"data: {json.dumps({'message': event['payload']})}\n\n"
                )
                    break

        except asyncio.CancelledError:
            print("[SSE] Client disconnected.")
            raise

        except Exception as exc:
            print(
                "[SSE EVENT GENERATOR ERROR] "
                f"{type(exc).__name__}: {exc}"
        )
            import traceback
            traceback.print_exc()

        # Do not report success when the stream failed.
            try:
                yield (
                    "event: error\n"
                    f"data: {json.dumps({'message': 'The response stream failed.'})}\n\n"
            )
            except Exception:
                pass