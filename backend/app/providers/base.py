import json
import uuid
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Sequence

from app.utils.prompt import ClientMessage

class BaseProvider(ABC):
    @abstractmethod
    async def stream_chat(
        self,
        messages: Sequence[ClientMessage],
        model: str,
        protocol: str = "data",
    ) -> AsyncGenerator[str, None]:
        """Stream chat responses in Vercel AI SDK format."""
        pass

    @staticmethod
    def format_sse(payload: dict) -> str:
        return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"

    @staticmethod
    def generate_id(prefix: str = "msg") -> str:
        return f"{prefix}-{uuid.uuid4().hex}"
