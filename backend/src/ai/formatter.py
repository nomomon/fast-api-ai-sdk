"""Converts AgentEvents to SSE format for the Vercel AI SDK."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from ai.agent.events import (
    Abort,
    AgentEvent,
    DataPart,
    Error,
    FilePart,
    Finish,
    FinishStep,
    MessageStart,
    ReasoningDelta,
    ReasoningEnd,
    ReasoningStart,
    SourceDocument,
    SourceUrl,
    StartStep,
    TextDelta,
    TextEnd,
    TextStart,
    ToolInputAvailable,
    ToolInputDelta,
    ToolInputStart,
    ToolOutputAvailable,
)
from fastapi.responses import StreamingResponse


def _event_to_dict(event: AgentEvent) -> dict:
    if isinstance(event, MessageStart):
        return {"type": "start", "messageId": event.message_id}
    elif isinstance(event, TextStart):
        return {"type": "text-start", "id": event.id}
    elif isinstance(event, TextDelta):
        return {"type": "text-delta", "id": event.id, "delta": event.delta}
    elif isinstance(event, TextEnd):
        return {"type": "text-end", "id": event.id}
    elif isinstance(event, ReasoningStart):
        return {"type": "reasoning-start", "id": event.id}
    elif isinstance(event, ReasoningDelta):
        return {"type": "reasoning-delta", "id": event.id, "delta": event.delta}
    elif isinstance(event, ReasoningEnd):
        return {"type": "reasoning-end", "id": event.id}
    elif isinstance(event, SourceUrl):
        return {"type": "source-url", "sourceId": event.source_id, "url": event.url}
    elif isinstance(event, SourceDocument):
        return {
            "type": "source-document",
            "sourceId": event.source_id,
            "mediaType": event.media_type,
            "title": event.title,
        }
    elif isinstance(event, FilePart):
        return {"type": "file", "url": event.url, "mediaType": event.media_type}
    elif isinstance(event, DataPart):
        return {"type": f"data-{event.data_type}", "data": event.data}
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
    elif isinstance(event, StartStep):
        return {"type": "start-step"}
    elif isinstance(event, FinishStep):
        return {"type": "finish-step"}
    elif isinstance(event, Finish):
        return {"type": "finish"}
    elif isinstance(event, Abort):
        return {"type": "abort", "reason": event.reason}
    elif isinstance(event, Error):
        return {"type": "error", "errorText": event.error_text}
    else:
        return {"type": "unknown"}


async def format_events(
    events: AsyncGenerator[AgentEvent, None],
) -> AsyncGenerator[str, None]:
    async for event in events:
        yield f"data: {json.dumps(_event_to_dict(event))}\n\n"
    yield "data: [DONE]\n\n"


def patch_response_with_headers(response: StreamingResponse) -> StreamingResponse:
    response.headers["x-vercel-ai-ui-message-stream"] = "v1"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    return response
