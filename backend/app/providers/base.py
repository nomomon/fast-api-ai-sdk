import uuid
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Sequence

from app.utils.prompt import ClientMessage
from app.utils.stream import StreamEvent


class BaseProvider(ABC):
    @abstractmethod
    async def stream_chat(
        self,
        messages: Sequence[ClientMessage],
        model: str,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream chat responses as structured events (dicts).

        Providers should yield dictionaries representing stream events.
        The SSE formatting is handled by the API layer.
        """
        pass

    @staticmethod
    def generate_id(prefix: str = "msg") -> str:
        return f"{prefix}-{uuid.uuid4().hex}"
