from fastapi import APIRouter, Depends, Request, HTTPException
from services.brain_service import BrainService
from api.dependencies import get_brain_service
from api.schemas.guest_schema import (
    GuestChatRequest,
    GuestChatResponse,
)
from services.guest_rate_limiter import guest_rate_limiter
from services.guest_session_service import guest_session_service
import asyncio
import json
import time

from fastapi.responses import StreamingResponse

from concurrent.futures import ThreadPoolExecutor

stream_executor = ThreadPoolExecutor(
    max_workers=10,
    thread_name_prefix="guest_stream",
)

router = APIRouter(
    prefix="/brain/guest",
    tags=["Guest Brain"],
)



@router.post("/chat", response_model=GuestChatResponse)
def guest_chat(
    request: GuestChatRequest,
    http_request: Request,
    brain_service: BrainService = Depends(get_brain_service),
):
    client_ip = (
        http_request.client.host
        if http_request.client
        else "unknown"
)

    allowed = guest_rate_limiter.allow_request(
        ip_key=client_ip,
        device_key=request.device_id,
)

    if not allowed:


        raise HTTPException(
            status_code=429,
            detail="Guest request limit reached. Please try again later.",
        )
    if not guest_session_service.reserve_turn(
        request.session_id
):
        raise HTTPException(
            status_code=403,
            detail="Guest limit reached. Please sign in to continue.",
    )

    response = brain_service.guest_chat(
        query=request.query,
        session_id=request.session_id,
    )
    turns_used = guest_session_service.get_turn_count(
        request.session_id
)

    turns_remaining = max(
        0,
        5 - turns_used
)

    return GuestChatResponse(
        response=response,
        turns_used=turns_used,
        turns_remaining=turns_remaining,
    )

@router.post("/chat/stream")
async def guest_chat_stream(
    request: GuestChatRequest,
    http_request: Request,
    brain_service: BrainService = Depends(get_brain_service),
):
    client_ip = (
        http_request.client.host
        if http_request.client
        else "unknown"
    )

    allowed = guest_rate_limiter.allow_request(
        ip_key=client_ip,
        device_key=request.device_id,
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Guest request limit reached. Please try again later.",
        )

    if not guest_session_service.reserve_turn(request.session_id):
        raise HTTPException(
            status_code=403,
            detail="Guest limit reached. Please sign in to continue.",
        )

    loop = asyncio.get_running_loop()
    event_queue = asyncio.Queue()
    executor = stream_executor

    def on_visual(payload):
        loop.call_soon_threadsafe(
            event_queue.put_nowait,
            {"type": "visual", "payload": payload},
        )

    def on_state(state):
        loop.call_soon_threadsafe(
            event_queue.put_nowait,
            {"type": "state", "payload": state},
        )


    def run_brain():
        try:
            for chunk in brain_service.guest_chat_stream(
                query=request.query,
                session_id=request.session_id,
                on_visual=on_visual,
                on_state=on_state,
            ):
                loop.call_soon_threadsafe(
                    event_queue.put_nowait,
                    {"type": "chunk", "payload": chunk},
                )

            turns_used = guest_session_service.get_turn_count(
                request.session_id
            )
            turns_remaining = max(0, 5 - turns_used)

            loop.call_soon_threadsafe(
                event_queue.put_nowait,
                {
                    "type": "metadata",
                    "payload": {
                        "turns_used": turns_used,
                        "turns_remaining": turns_remaining,
                    },
                },
            )

            loop.call_soon_threadsafe(
                event_queue.put_nowait,
                {"type": "text_complete"},
            )

        except Exception as exc:
            loop.call_soon_threadsafe(
                event_queue.put_nowait,
                {"type": "error", "payload": str(exc)},
            )

        finally:
            loop.call_soon_threadsafe(
                event_queue.put_nowait,
                {"type": "complete"},
            )



    executor_future = loop.run_in_executor(executor, run_brain)

    async def event_generator():
        while True:
            event = await event_queue.get()
            event_type = event["type"]

            if event_type == "chunk":
                yield (
                    "event: chunk\n"
                    f"data: {json.dumps({'text': event['payload']})}\n\n"
                )

            elif event_type == "visual":
                yield (
                    "event: visual\n"
                    f"data: {json.dumps({'visual': event['payload']})}\n\n"
                )

            elif event_type == "state":
                yield (
                    "event: state\n"
                    f"data: {json.dumps({'state': event['payload']})}\n\n"
                )

            elif event_type == "text_complete":
                yield 'event: text_complete\ndata: {"success": true}\n\n'

            elif event_type == "error":
                yield (
                    "event: error\n"
                    f"data: {json.dumps({'message': event['payload']})}\n\n"
                )
                break

            elif event_type == "complete":
                yield 'event: complete\ndata: {"success": true}\n\n'
                break
            elif event_type == "metadata":
                yield (
                "event: metadata\n"
               f"data: {json.dumps(event['payload'])}\n\n"
    )


    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
