import json
import os
import uuid
from collections.abc import AsyncGenerator, Sequence
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

import litellm

from app.config import settings
from app.utils.prompt import ClientMessage, convert_to_openai_messages
from app.utils.stream import StreamEvent
from app.utils.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS


class StreamState(Enum):
    """State machine for streaming conversation flow."""

    INITIAL = auto()
    STREAMING = auto()
    PROCESSING_TOOLS = auto()
    FINISHED = auto()
    ERROR = auto()


@dataclass
class StreamStateData:
    """Data class for tracking stream state during processing."""

    text_started: bool = False
    reasoning_started: bool = False
    finish_reason: str | None = None
    current_text_content: str = ""
    tool_calls_state: dict[int, dict[str, Any]] = field(default_factory=dict)


class ChunkProcessor:
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
        delta: Any,
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
        delta: Any,
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
        tool_call_delta: Any,
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


class LiteLLMProvider(ChunkProcessor):
    """LiteLLM provider implementation with state machine for stream processing."""

    # Constants for stream IDs
    TEXT_STREAM_ID = "text-1"
    REASONING_STREAM_ID = "reasoning-1"

    def __init__(self, provider_name: str):
        """Initialize the LiteLLM provider.

        Args:
            provider_name: The name of the provider (e.g., 'openai', 'gemini')
        """
        self.provider_name = provider_name

        # Ensure environment variables are set for LiteLLM
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        if settings.gemini_api_key:
            os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
        # Add other providers here as needed

    def _build_reasoning_effort(self, full_model_name: str) -> dict[str, str] | str | None:
        """Build the reasoning effort configuration for the model.

        Args:
            full_model_name: The full model name including provider prefix

        Returns:
            Reasoning effort configuration dict, string, or None
        """
        if not litellm.supports_reasoning(model=full_model_name):
            return None

        if "/responses/" in full_model_name:
            return {"effort": "low", "summary": "detailed"}
        return "low"

    async def stream_chat(
        self,
        messages: Sequence[ClientMessage],
        model: str,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream chat responses as structured events.

        Uses a state machine to manage the conversation flow:
        - INITIAL -> STREAMING (after start event)
        - STREAMING -> PROCESSING_TOOLS (when tool calls detected)
        - PROCESSING_TOOLS -> STREAMING (after tool execution, continue conversation)
        - STREAMING -> FINISHED (when no tool calls, normal completion)
        - Any state -> ERROR (on exceptions)

        Args:
            messages: Sequence of client messages
            model: Model name to use

        Yields:
            Stream events (dicts) representing the conversation flow
        """
        openai_messages = convert_to_openai_messages(messages)
        tool_definitions = TOOL_DEFINITIONS
        available_tools = AVAILABLE_TOOLS

        state_machine = StreamState.INITIAL
        stream_state: StreamStateData | None = None

        try:
            message_id = self.generate_id()
            text_stream_id = self.TEXT_STREAM_ID
            reasoning_stream_id = self.REASONING_STREAM_ID

            yield {"type": "start", "messageId": message_id}
            state_machine = StreamState.STREAMING

            # Construct the model string expected by LiteLLM
            full_model_name = f"{self.provider_name}/{model}"

            reasoning_effort = self._build_reasoning_effort(full_model_name)

            while state_machine == StreamState.STREAMING:
                # Initialize state for this iteration
                stream_state = StreamStateData()
                tool_calls_state = stream_state.tool_calls_state

                stream = await litellm.acompletion(
                    model=full_model_name,
                    messages=openai_messages,
                    stream=True,
                    tools=tool_definitions if tool_definitions else None,
                    reasoning_effort=reasoning_effort,
                )

                async for chunk in stream:
                    if not chunk.choices:
                        continue

                    choice = chunk.choices[0]

                    if choice.finish_reason is not None:
                        stream_state.finish_reason = choice.finish_reason

                    delta = choice.delta
                    if delta is None:
                        continue

                    # Process reasoning content
                    async for event in self._process_reasoning_chunk(
                        delta, stream_state, reasoning_stream_id
                    ):
                        yield event

                    # Process text content
                    async for event in self._process_text_chunk(
                        delta, stream_state, text_stream_id
                    ):
                        yield event

                    # Process tool calls
                    if delta.tool_calls:
                        for tool_call_delta in delta.tool_calls:
                            async for event in self._process_tool_call_chunk(
                                tool_call_delta, tool_calls_state
                            ):
                                yield event

                # If no tool calls were collected, we are done
                if not tool_calls_state:
                    state_machine = StreamState.FINISHED
                    break

                # If we have tool calls, process them and continue the loop
                state_machine = StreamState.PROCESSING_TOOLS

                assistant_message_tool_calls = []
                tool_results_messages = []

                async for event in self._process_tool_calls(
                    tool_calls_state,
                    available_tools,
                    assistant_message_tool_calls,
                    tool_results_messages,
                ):
                    yield event

                # Append assistant message with ALL tool calls
                openai_messages.append(
                    {
                        "role": "assistant",
                        "content": stream_state.current_text_content
                        if stream_state.current_text_content
                        else None,
                        "tool_calls": assistant_message_tool_calls,
                    }
                )

                # Append tool results
                openai_messages.extend(tool_results_messages)

                # Continue streaming with updated messages
                state_machine = StreamState.STREAMING

            if state_machine == StreamState.FINISHED and stream_state is not None:
                yield {"type": "finish", "finishReason": stream_state.finish_reason}

        except Exception as e:
            state_machine = StreamState.ERROR
            print(f"Error in stream_chat: {e}")
            yield {"type": "error", "error": str(e)}
