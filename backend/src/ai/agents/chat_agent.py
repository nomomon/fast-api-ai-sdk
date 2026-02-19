"""Chat completion agent implementation."""

import logging
import os
from collections.abc import AsyncGenerator, Sequence
from typing import Any

import litellm

from src.ai.adapters.messages import ClientMessage, convert_to_openai_messages
from src.ai.adapters.streaming import StreamEvent
from src.ai.agents.base import BaseAgent
from src.ai.streaming.processor import StreamChunkProcessor
from src.ai.streaming.state import (
    REASONING_STREAM_ID,
    TEXT_STREAM_ID,
    StreamState,
    StreamStateData,
)
from src.ai.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS
from src.config import settings

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):
    """Chat completion agent with state machine for stream processing."""

    def __init__(self, model_id: str):
        """Initialize the chat agent."""
        self.model_id = model_id
        self._processor = StreamChunkProcessor()
        self._setup_environment()

    def _setup_environment(self) -> None:
        """Set up environment variables for LiteLLM."""
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        if settings.gemini_api_key:
            os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

    def _build_reasoning_effort(self, full_model_name: str) -> dict[str, str] | str | None:
        """Build the reasoning effort configuration for the model."""
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
        """Process chunks from the LLM stream."""
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

            async for event in self._processor._process_reasoning_chunk(
                delta, stream_state, reasoning_stream_id
            ):
                yield event

            async for event in self._processor._process_text_chunk(
                delta, stream_state, text_stream_id
            ):
                yield event

            async for event in self._processor._process_content_parts(delta):
                yield event

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
        """Process tool calls and update message history."""
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

        openai_messages.append(
            {
                "role": "assistant",
                "content": stream_state.current_text_content
                if stream_state.current_text_content
                else None,
                "tool_calls": assistant_message_tool_calls,
            }
        )

        openai_messages.extend(tool_results_messages)

    async def execute(self, messages: Sequence[ClientMessage]) -> AsyncGenerator[StreamEvent, None]:
        """Execute the chat agent workflow."""
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
                stream_state = StreamStateData()
                tool_calls_state = stream_state.tool_calls_state

                stream = await litellm.acompletion(
                    model=self.model_id,
                    messages=openai_messages,
                    stream=True,
                    tools=tool_definitions if tool_definitions else None,
                    reasoning_effort=reasoning_effort,
                )

                async for event in self._process_stream_chunks(
                    stream, stream_state, text_stream_id, reasoning_stream_id
                ):
                    yield event

                if not tool_calls_state:
                    state_machine = StreamState.FINISHED
                    break

                state_machine = StreamState.PROCESSING_TOOLS

                async for event in self._process_tool_calls_and_update_messages(
                    stream_state, available_tools, openai_messages
                ):
                    yield event

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
        """Stream chat responses as structured events."""
        async for event in self.execute(messages):
            yield event
