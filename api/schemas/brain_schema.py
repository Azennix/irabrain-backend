from datetime import datetime
from typing import Literal
from decimal import Decimal
from pydantic import BaseModel, Field

class BrainAttachment(BaseModel):

    type: str
    name: str | None = None
    content: str | None = None
    data: str | None = None
    mime_type: str | None = None

class TextResponseBlock(BaseModel):
    id: str
    type: Literal["text"]
    content: str


class VisualResponseBlock(BaseModel):
    id: str
    type: Literal["visual"]
    visual: dict


class IRAResponseBlocks(BaseModel):
    version: Literal[2] = 2
    blocks: list[TextResponseBlock | VisualResponseBlock] = Field(
        default_factory=list
    )


class BrainChatRequest(BaseModel):

    query: str
    conversation_id: str | None = None
    project_id: str | None = None
    session_id: str | None = None

    attachments: list[BrainAttachment] = Field(default_factory=list)
    workspace_mode: Literal["personal", "private"] = "personal"

class UpdateMemoryRequest(BaseModel):
    category: str
    key: str
    value: str

class ConversationMessageResponse(BaseModel):

    message_id: int
    role: str
    content: str
    visual_data: dict | None = None
    response_blocks: IRAResponseBlocks | None = None


class ConversationResponse(BaseModel):

    messages: list[ConversationMessageResponse]

class CreateConversationRequest(BaseModel):

    title: str = "New Conversation"


class ConversationSummaryResponse(BaseModel):

    conversation_id: str
    title: str
    created_at: datetime
    updated_at: datetime

class CreateProjectRequest(BaseModel):
    name: str
    description: str | None = None


class UpdateProjectRequest(BaseModel):
    name: str
    description: str | None = None
    status: str


class CreateGoalRequest(BaseModel):

    title: str
    description: str | None = None


class UpdateGoalRequest(BaseModel):
    title: str
    description: str | None = None
    status: str
class CreateTaskRequest(BaseModel):
    title: str
    description: str | None = None
    goal_id: str | None = None


class UpdateTaskRequest(BaseModel):
    title: str
    description: str | None = None
    status: str
    goal_id: str | None = None


class CreateDecisionRequest(BaseModel):
    title: str
    description: str | None = None
    reason: str | None = None


class UpdateDecisionRequest(BaseModel):
    title: str
    description: str | None = None
    reason: str | None = None
    status: str

class BrainBalanceResponse(BaseModel):
    user_id: int
    included_balance: Decimal
    paid_balance: Decimal
    total_balance: Decimal
    next_reset_at: datetime | None = None
    reset_interval_hours: int | None = None