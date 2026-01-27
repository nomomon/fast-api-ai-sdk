import os
from collections.abc import AsyncGenerator, Sequence
from enum import Enum, auto

import litellm

from app.config import settings
from app.providers.someclass import ChunkProcessor, StreamStateData
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
