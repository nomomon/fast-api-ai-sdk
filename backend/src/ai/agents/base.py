"""Base agent interface for all agent types."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Sequence

from src.ai.adapters.messages import ClientMessage
from src.ai.adapters.streaming import StreamEvent


class BaseAgent(ABC):
    """Base interface for all agent types."""

    @abstractmethod
    async def execute(self, messages: Sequence[ClientMessage]) -> AsyncGenerator[StreamEvent, None]:
        """Execute the agent workflow."""
        pass
