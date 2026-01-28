"""Base agent interface for all agent types."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Sequence

from app.adapters.messages import ClientMessage
from app.adapters.streaming import StreamEvent


class BaseAgent(ABC):
    """Base interface for all agent types."""

    @abstractmethod
    async def execute(self, messages: Sequence[ClientMessage]) -> AsyncGenerator[StreamEvent, None]:
        """Execute the agent workflow.

        Args:
            messages: Sequence of client messages

        Yields:
            Stream events representing the agent's execution flow
        """
        pass
