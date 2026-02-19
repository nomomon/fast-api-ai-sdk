"""Chat request/response schemas."""

from pydantic import BaseModel

from src.ai.adapters.messages import ClientMessage


class ChatRequest(BaseModel):
    """Chat request schema."""

    messages: list[ClientMessage]
    modelId: str | None = None
    promptId: str | None = None
    agentId: str = "chat"
