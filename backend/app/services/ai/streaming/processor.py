"""Stream chunk processor for LLM responses."""

import json
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from app.adapters.streaming import StreamEvent
from app.services.ai.streaming.protocols import DeltaContent, ToolCallDelta
from app.services.ai.streaming.state import StreamStateData


class StreamChunkProcessor:
    """Base class for processing streaming chunks from LLM responses."""

    @staticmethod
    def generate_id(prefix: str = "msg") -> str:
        """Generate a unique ID with optional prefix.

        Args:
            prefix: Prefix for the ID (default: "msg")

        Returns:
            Unique ID string
        """
        return f"{prefix}-{uuid.uuid4().hex}"

    async def _process_reasoning_chunk(
        self,
        delta: DeltaContent,
        state: StreamStateData,
        reasoning_stream_id: str,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Process reasoning content from a chunk delta.

        Args:
            delta: The delta object from the chunk
            state: Current stream state data
            reasoning_stream_id: ID for the reasoning stream

        Yields:
            Stream events for reasoning content
        """
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
        """Process text content from a chunk delta.

        Args:
            delta: The delta object from the chunk
            state: Current stream state data
            text_stream_id: ID for the text stream

        Yields:
            Stream events for text content
        """
        if delta.content is not None:
            state.current_text_content += delta.content
            if not state.text_started:
                yield {"type": "text-start", "id": text_stream_id}
                state.text_started = True
            yield {"type": "text-delta", "id": text_stream_id, "delta": delta.content}

    async def _process_tool_call_chunk(
        self,
        tool_call_delta: ToolCallDelta,
        tool_calls_state: dict[int, dict[str, Any]],
    ) -> AsyncGenerator[StreamEvent, None]:
        """Process a tool call delta from a chunk.

        Args:
            tool_call_delta: The tool call delta object
            tool_calls_state: Dictionary tracking tool call state by index

        Yields:
            Stream events for tool call processing
        """
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
        """Process tool calls by executing them and building response messages.

        Args:
            tool_calls_state: Dictionary of tool call states by index
            available_tools: Dictionary of available tool functions
            assistant_message_tool_calls: List to populate with assistant tool call messages
            tool_results_messages: List to populate with tool result messages

        Yields:
            Stream events for tool execution
        """
        for state in tool_calls_state.values():
            tool_call_id = state["id"]
            tool_name = state["name"]
            arguments_str = state["arguments"]

            # Ensure we have a valid tool_call_id for error reporting
            if tool_call_id is None:
                continue

            try:
                arguments = json.loads(arguments_str)

                # Reconstruct the tool call object for the assistant message
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
