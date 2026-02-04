"""Chat completion agent implementation."""

import logging
import os
from collections.abc import AsyncGenerator, Sequence
from typing import Any

import litellm

from app.core.config import settings
from app.services.ai.adapters.messages import ClientMessage, convert_to_openai_messages
from app.services.ai.adapters.streaming import StreamEvent
from app.services.ai.agents.base import BaseAgent
from app.services.ai.streaming.processor import StreamChunkProcessor
from app.services.ai.streaming.state import (
    REASONING_STREAM_ID,
    TEXT_STREAM_ID,
    StreamState,
    StreamStateData,
)
from app.services.ai.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):
    """Chat completion agent with state machine for stream processing."""

    def __init__(
        self,
        model_id: str,
    ):
        """Initialize the chat agent.

        Args:
            model_id: The model identifier (e.g., 'openai/gpt-4', 'gemini/gemini-pro')
        """
        self.model_id = model_id
        self._processor = StreamChunkProcessor()
        self._setup_environment()

    def _setup_environment(self) -> None:
        """Set up environment variables for LiteLLM.

        This method is separated from __init__ to improve testability
        and avoid side effects during initialization.
        """
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

    async def _process_stream_chunks(
        self,
        stream: AsyncGenerator[Any, None],
        stream_state: StreamStateData,
        text_stream_id: str,
        reasoning_stream_id: str,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Process chunks from the LLM stream.

        Args:
            stream: The async generator from litellm.acompletion
            stream_state: Current stream state data
            text_stream_id: ID for the text stream
            reasoning_stream_id: ID for the reasoning stream

        Yields:
            Stream events from processing chunks
        """
        tool_calls_state = stream_state.tool_calls_state

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
            async for event in self._processor._process_reasoning_chunk(
                delta, stream_state, reasoning_stream_id
            ):
                yield event

            # Process text content
            async for event in self._processor._process_text_chunk(
                delta, stream_state, text_stream_id
            ):
                yield event

            # Process content parts (file references from multimodal streams)
            async for event in self._processor._process_content_parts(delta):
                yield event

            # Process tool calls
            if delta.tool_calls:
                for tool_call_delta in delta.tool_calls:
                    async for event in self._processor._process_tool_call_chunk(
                        tool_call_delta, tool_calls_state
                    ):
                        yield event

    async def _process_tool_calls_and_update_messages(
        self,
        stream_state: StreamStateData,
        available_tools: dict[str, Any],
        openai_messages: list[dict[str, Any]],
    ) -> AsyncGenerator[StreamEvent, None]:
        """Process tool calls and update message history.

        Args:
            stream_state: Current stream state data
            available_tools: Dictionary of available tool functions
            openai_messages: List of messages to update

        Yields:
            Stream events from tool processing
        """
        tool_calls_state = stream_state.tool_calls_state
        assistant_message_tool_calls = []
        tool_results_messages = []

        async for event in self._processor._process_tool_calls(
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

    async def execute(self, messages: Sequence[ClientMessage]) -> AsyncGenerator[StreamEvent, None]:
        """Execute the chat agent workflow.

        Uses a state machine to manage the conversation flow:
        - INITIAL -> STREAMING (after start event)
        - STREAMING -> PROCESSING_TOOLS (when tool calls detected)
        - PROCESSING_TOOLS -> STREAMING (after tool execution, continue conversation)
        - STREAMING -> FINISHED (when no tool calls, normal completion)
        - Any state -> ERROR (on exceptions)

        Args:
            messages: Sequence of client messages

        Yields:
            Stream events (dicts) representing the conversation flow
        """
        openai_messages = convert_to_openai_messages(messages)
        tool_definitions = TOOL_DEFINITIONS
        available_tools = AVAILABLE_TOOLS

        state_machine = StreamState.INITIAL
        stream_state: StreamStateData | None = None

        try:
            message_id = self._processor.generate_id()
            text_stream_id = TEXT_STREAM_ID
            reasoning_stream_id = REASONING_STREAM_ID

            yield {"type": "start", "messageId": message_id}
            state_machine = StreamState.STREAMING

            reasoning_effort = self._build_reasoning_effort(self.model_id)

            while state_machine == StreamState.STREAMING:
                # Initialize state for this iteration
                stream_state = StreamStateData()
                tool_calls_state = stream_state.tool_calls_state

                stream = await litellm.acompletion(
                    model=self.model_id,
                    messages=openai_messages,
                    stream=True,
                    tools=tool_definitions if tool_definitions else None,
                    reasoning_effort=reasoning_effort,
                )

                # Process all chunks from the stream
                async for event in self._process_stream_chunks(
                    stream, stream_state, text_stream_id, reasoning_stream_id
                ):
                    yield event

                # If no tool calls were collected, we are done
                if not tool_calls_state:
                    state_machine = StreamState.FINISHED
                    break

                # If we have tool calls, process them and continue the loop
                state_machine = StreamState.PROCESSING_TOOLS

                async for event in self._process_tool_calls_and_update_messages(
                    stream_state, available_tools, openai_messages
                ):
                    yield event

                # Continue streaming with updated messages
                state_machine = StreamState.STREAMING

            if state_machine == StreamState.FINISHED and stream_state is not None:
                yield {"type": "finish", "finishReason": stream_state.finish_reason}

        except Exception as e:
            state_machine = StreamState.ERROR
            logger.error(f"Error in chat agent execution: {e}", exc_info=True)
            yield {"type": "error", "error": str(e)}

    async def stream_chat(
        self, messages: Sequence[ClientMessage]
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream chat responses as structured events.

        This method is kept for backward compatibility.
        It delegates to execute().

        Args:
            messages: Sequence of client messages

        Yields:
            Stream events (dicts) representing the conversation flow
        """
        async for event in self.execute(messages):
            yield event
