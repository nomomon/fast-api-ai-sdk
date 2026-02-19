"""Stream chunk processor for LLM responses."""

import asyncio
import json
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from src.ai.adapters.streaming import StreamEvent
from src.ai.streaming.protocols import DeltaContent, ToolCallDelta
from src.ai.streaming.state import StreamStateData


class StreamChunkProcessor:
    """Base class for processing streaming chunks from LLM responses."""

    @staticmethod
    def generate_id(prefix: str = "msg") -> str:
        """Generate a unique ID with optional prefix."""
        return f"{prefix}-{uuid.uuid4().hex}"

    async def _process_reasoning_chunk(
        self,
        delta: DeltaContent,
        state: StreamStateData,
        reasoning_stream_id: str,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Process reasoning content from a chunk delta."""
        reasoning_content = getattr(delta, "reasoning_content", None)
        if reasoning_content is not None:
            if not state.reasoning_started:
                yield {"type": "reasoning-start", "id": reasoning_stream_id}
                state.reasoning_started = True
            yield {
                "type": "reasoning-delta",
                "id": reasoning_stream_id,
                "delta": reasoning_content,
            }

    async def _process_text_chunk(
        self,
        delta: DeltaContent,
        state: StreamStateData,
        text_stream_id: str,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Process text content from a chunk delta."""
        if delta.content is not None:
            state.current_text_content += delta.content
            if not state.text_started:
                yield {"type": "text-start", "id": text_stream_id}
                state.text_started = True
            yield {"type": "text-delta", "id": text_stream_id, "delta": delta.content}

    async def _process_file_part(
        self,
        url: str,
        media_type: str,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Emit a file part event."""
        yield {"type": "file", "url": url, "mediaType": media_type}

    async def _process_data_part(
        self,
        type_suffix: str,
        data: dict[str, Any],
    ) -> AsyncGenerator[StreamEvent, None]:
        """Emit a custom data part event."""
        yield {"type": f"data-{type_suffix}", "data": data}

    async def _process_content_parts(
        self,
        delta: DeltaContent,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Process content parts from delta."""
        content_parts = getattr(delta, "content_parts", None)
        if not content_parts:
            return

        for part in content_parts:
            if not isinstance(part, dict):
                continue
            part_type = part.get("type")
            if part_type == "image_url":
                image_url = part.get("image_url") or {}
                url = image_url.get("url") if isinstance(image_url, dict) else None
                if url:
                    media_type = "image/png"
                    if ".jpg" in url or ".jpeg" in url:
                        media_type = "image/jpeg"
                    elif ".gif" in url:
                        media_type = "image/gif"
                    elif ".webp" in url:
                        media_type = "image/webp"
                    async for event in self._process_file_part(url, media_type):
                        yield event

    async def _process_tool_call_chunk(
        self,
        tool_call_delta: ToolCallDelta,
        tool_calls_state: dict[int, dict[str, Any]],
    ) -> AsyncGenerator[StreamEvent, None]:
        """Process a tool call delta from a chunk."""
        index = tool_call_delta.index
        state = tool_calls_state.setdefault(
            index,
            {
                "id": None,
                "name": None,
                "arguments": "",
                "started": False,
            },
        )

        if tool_call_delta.id is not None:
            state["id"] = tool_call_delta.id

        if tool_call_delta.function:
            if tool_call_delta.function.name:
                state["name"] = tool_call_delta.function.name

            if tool_call_delta.function.arguments:
                state["arguments"] += tool_call_delta.function.arguments

        if state["id"] is not None and state["name"] is not None and not state["started"]:
            yield {
                "type": "tool-input-start",
                "toolCallId": state["id"],
                "toolName": state["name"],
            }
            state["started"] = True

        if state["started"] and tool_call_delta.function and tool_call_delta.function.arguments:
            yield {
                "type": "tool-input-delta",
                "toolCallId": state["id"],
                "inputTextDelta": tool_call_delta.function.arguments,
            }

    async def _process_tool_calls(
        self,
        tool_calls_state: dict[int, dict[str, Any]],
        available_tools: dict[str, Any],
        assistant_message_tool_calls: list[dict[str, Any]],
        tool_results_messages: list[dict[str, Any]],
    ) -> AsyncGenerator[StreamEvent, None]:
        """Process tool calls by executing them and building response messages."""
        for state in tool_calls_state.values():
            tool_call_id = state["id"]
            tool_name = state["name"]
            arguments_str = state["arguments"]

            if tool_call_id is None:
                continue

            try:
                arguments = json.loads(arguments_str)

                assistant_message_tool_calls.append(
                    {
                        "id": tool_call_id,
                        "type": "function",
                        "function": {"name": tool_name, "arguments": arguments_str},
                    }
                )

                yield {
                    "type": "tool-input-available",
                    "toolCallId": tool_call_id,
                    "toolName": tool_name,
                    "input": arguments,
                }

                tool_func = available_tools.get(tool_name)
                tool_result = None

                if tool_func:
                    if asyncio.iscoroutinefunction(tool_func):
                        tool_result = await tool_func(**arguments)
                    else:
                        tool_result = tool_func(**arguments)
                    yield {
                        "type": "tool-output-available",
                        "toolCallId": tool_call_id,
                        "output": tool_result,
                    }
                else:
                    tool_result = {"error": f"Tool {tool_name} not found"}
                    yield {
                        "type": "tool-output-available",
                        "toolCallId": tool_call_id,
                        "output": tool_result,
                    }

                if isinstance(tool_result, dict):
                    url = tool_result.get("url")
                    media_type = tool_result.get("mediaType") or tool_result.get("media_type")
                    if url and media_type:
                        async for event in self._process_file_part(url, media_type):
                            yield event

                tool_results_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": json.dumps(tool_result)
                        if not isinstance(tool_result, str)
                        else tool_result,
                    }
                )

            except json.JSONDecodeError:
                yield {
                    "type": "tool-output-available",
                    "toolCallId": tool_call_id,
                    "output": {"error": "Failed to parse arguments"},
                }
