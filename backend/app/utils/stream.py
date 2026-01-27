import json
from collections.abc import AsyncGenerator
from typing import Any

from fastapi.responses import StreamingResponse

# Type alias for stream events - providers yield dicts with these structures
StreamEvent = dict[str, Any]


class SSEFormatter:
    """Formats structured stream events into Server-Sent Events (SSE) format."""

    @staticmethod
    def format_event(event: StreamEvent) -> str:
        """Convert a stream event dictionary to SSE format string."""
        return f"data: {json.dumps(event, separators=(',', ':'))}\n\n"

    @staticmethod
    async def format_stream(
        stream: AsyncGenerator[StreamEvent, None],
    ) -> AsyncGenerator[str, None]:
        """Wrap a provider stream to convert events to SSE format."""
        async for event in stream:
            yield SSEFormatter.format_event(event)


def patch_response_with_headers(
    response: StreamingResponse,
) -> StreamingResponse:
    """Apply the standard streaming headers expected by the Vercel AI SDK."""

    response.headers["x-vercel-ai-ui-message-stream"] = "v1"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"

    return response
