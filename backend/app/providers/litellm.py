import json
import os
from collections.abc import Sequence
from typing import Any

import litellm
from app.config import settings
from app.providers.base import BaseProvider
from app.utils.prompt import ClientMessage, convert_to_openai_messages
from app.utils.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS


class LiteLLMProvider(BaseProvider):
    def __init__(self, provider_name: str):
        self.provider_name = provider_name

        # Ensure environment variables are set for LiteLLM
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        if settings.gemini_api_key:
            os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
        # Add other providers here as needed

    async def stream_chat(
        self,
        messages: Sequence[ClientMessage],
        model: str,
        protocol: str = "data",
    ):
        openai_messages = convert_to_openai_messages(messages)
        tool_definitions = TOOL_DEFINITIONS
        available_tools = AVAILABLE_TOOLS

        try:
            message_id = self.generate_id()
            text_stream_id = "text-1"
            text_started = False
            reasoning_stream_id = "reasoning-1"
            reasoning_started = False
            finish_reason = None
            tool_calls_state: dict[int, dict[str, Any]] = {}

            yield self.format_sse({"type": "start", "messageId": message_id})

            # Construct the model string expected by LiteLLM (e.g., "openai/gpt-4o", "gemini/gemini-1.5-flash")
            full_model_name = f"{self.provider_name}/{model}"
            
            # Special handling for Gemini thinking if needed or other provider specifics
            # For now, we rely on LiteLLM's abstraction
            
            stream = await litellm.acompletion(
                model=full_model_name,
                messages=openai_messages,
                stream=True,
                tools=tool_definitions if tool_definitions else None,
            )

            async for chunk in stream:
                if not chunk.choices:
                    continue
                
                choice = chunk.choices[0]
                
                if choice.finish_reason is not None:
                    finish_reason = choice.finish_reason

                delta = choice.delta
                if delta is None:
                    continue

                # Handle reasoning content (DeepSeek/Reasoning models)
                # LiteLLM standardizes this field if present
                reasoning_content = getattr(delta, "reasoning_content", None)
                if reasoning_content is not None:
                    if not reasoning_started:
                        yield self.format_sse(
                            {"type": "reasoning-start", "id": reasoning_stream_id}
                        )
                        reasoning_started = True
                    yield self.format_sse(
                        {
                            "type": "reasoning-delta",
                            "id": reasoning_stream_id,
                            "delta": reasoning_content,
                        }
                    )

                if delta.content is not None:
                    if not text_started:
                        yield self.format_sse({"type": "text-start", "id": text_stream_id})
                        text_started = True
                    yield self.format_sse(
                        {"type": "text-delta", "id": text_stream_id, "delta": delta.content}
                    )

                if delta.tool_calls:
                    for tool_call_delta in delta.tool_calls:
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
                            # If we have ID and Name, and haven't started, emit start
                            # Wait, usually ID comes first. logic below handles names split across chunks too?
                        
                        if tool_call_delta.function:
                            if tool_call_delta.function.name:
                                state["name"] = tool_call_delta.function.name
                            
                            if tool_call_delta.function.arguments:
                                state["arguments"] += tool_call_delta.function.arguments

                        if (
                            state["id"] is not None
                            and state["name"] is not None
                            and not state["started"]
                        ):
                            yield self.format_sse(
                                {
                                    "type": "tool-call-start",
                                    "toolCallId": state["id"],
                                    "toolName": state["name"],
                                }
                            )
                            state["started"] = True
                        
                        if state["started"] and tool_call_delta.function and tool_call_delta.function.arguments:
                             yield self.format_sse(
                                {
                                    "type": "tool-call-delta",
                                    "toolCallId": state["id"],
                                    "argsTextDelta": tool_call_delta.function.arguments,
                                }
                            )

            if finish_reason == "tool_calls":
                for index, state in tool_calls_state.items():
                    tool_call_id = state["id"]
                    tool_name = state["name"]
                    arguments_str = state["arguments"]
                    
                    try:
                        arguments = json.loads(arguments_str)
                        
                        tool_func = available_tools.get(tool_name)
                        if tool_func:
                            yield self.format_sse(
                                {
                                    "type": "tool-call-result",
                                    "toolCallId": tool_call_id,
                                    "result": tool_func(**arguments),
                                }
                            )
                        else:
                             yield self.format_sse(
                                {
                                    "type": "tool-call-result",
                                    "toolCallId": tool_call_id,
                                    "result": {"error": f"Tool {tool_name} not found"},
                                }
                             )

                    except json.JSONDecodeError:
                         yield self.format_sse(
                            {
                                "type": "tool-call-result",
                                "toolCallId": tool_call_id,
                                "result": {"error": "Failed to parse arguments"},
                            }
                        )
                
            yield self.format_sse({"type": "finish", "finishReason": finish_reason})

        except Exception as e:
            print(f"Error in stream_chat: {e}")
            yield self.format_sse({"type": "error", "error": str(e)})
