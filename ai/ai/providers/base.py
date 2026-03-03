"""Abstract LLM provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCallDelta:
    index: int
    id: str | None = None
    name: str | None = None
    arguments: str = ""


@dataclass
class ChunkDelta:
    content: str | None = None
    tool_calls: list[ToolCallDelta] = field(default_factory=list)
    finish_reason: str | None = None


class LLMProvider(ABC):
    """Abstract base for LLM providers.

    Implementations wrap a specific SDK (litellm, openai, anthropic, etc.)
    and yield normalized ChunkDelta objects. The agent loop is responsible
    for interpreting deltas and emitting typed AgentEvents.
    """

    @abstractmethod
    async def stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        model: str,
    ) -> AsyncGenerator[ChunkDelta, None]:
        """Stream parsed chunk deltas from the LLM."""
