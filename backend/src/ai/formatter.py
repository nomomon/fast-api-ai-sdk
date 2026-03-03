"""Converts AgentEvents to SSE format for the Vercel AI SDK."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from fastapi.responses import StreamingResponse

from ai.agent.events import (
    AgentEvent,
    Error,
    Finish,
    TextDelta,
    TextStart,
    ToolInputAvailable,
    ToolInputDelta,
    ToolInputStart,
    ToolOutputAvailable,
)


def _event_to_dict(event: AgentEvent) -> dict:
    if isinstance(event, TextStart):
        return {"type": "text-start"}
    elif isinstance(event, TextDelta):
        return {"type": "text-delta", "textDelta": event.delta}
    elif isinstance(event, ToolInputStart):
        return {
            "type": "tool-input-start",
            "toolCallId": event.tool_call_id,
            "toolName": event.tool_name,
        }
    elif isinstance(event, ToolInputDelta):
        return {
            "type": "tool-input-delta",
            "toolCallId": event.tool_call_id,
            "inputTextDelta": event.input_text_delta,
        }
    elif isinstance(event, ToolInputAvailable):
        return {
            "type": "tool-input-available",
            "toolCallId": event.tool_call_id,
            "toolName": event.tool_name,
            "input": event.input,
        }
    elif isinstance(event, ToolOutputAvailable):
        return {
            "type": "tool-output-available",
            "toolCallId": event.tool_call_id,
            "output": event.output,
        }
    elif isinstance(event, Finish):
        return {"type": "finish", "finishReason": event.finish_reason}
    elif isinstance(event, Error):
        return {"type": "error", "error": event.error}
    else:
        return {"type": "unknown"}


async def format_events(
    events: AsyncGenerator[AgentEvent, None],
) -> AsyncGenerator[str, None]:
    async for event in events:
        yield f"data: {json.dumps(_event_to_dict(event))}\n\n"


def patch_response_with_headers(response: StreamingResponse) -> StreamingResponse:
    response.headers["x-vercel-ai-ui-message-stream"] = "v1"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    return response
