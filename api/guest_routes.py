from fastapi import APIRouter, Depends, Request, HTTPException
from services.brain_service import BrainService
from api.dependencies import get_brain_service
from api.schemas.guest_schema import (
    GuestChatRequest,
    GuestChatResponse,
)
from services.guest_rate_limiter import guest_rate_limiter
from services.guest_session_service import guest_session_service

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