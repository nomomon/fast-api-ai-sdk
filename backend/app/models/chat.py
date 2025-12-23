
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message model."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    messages: list[Message] = Field(..., description="List of chat messages")
    temperature: float | None = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int | None = Field(1000, ge=1, le=4000, description="Maximum tokens in response")
    stream: bool | None = Field(False, description="Whether to stream the response")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    message: str = Field(..., description="Response message")
    role: str = Field(default="assistant", description="Message role")
