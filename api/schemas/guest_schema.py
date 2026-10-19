from pydantic import BaseModel, Field


# =====================================================
# GUEST CHAT REQUEST
# =====================================================

class GuestChatRequest(BaseModel):

    session_id: str = Field(
        min_length=1,
        max_length=128,
    )

    device_id: str = Field(
        min_length=1,
        max_length=256,
    )

    query: str = Field(
        min_length=1,
        max_length=10000,
    )


# =====================================================
# GUEST CHAT RESPONSE
# =====================================================

class GuestChatResponse(BaseModel):

    response: str

    turns_used: int

    turns_remaining: int