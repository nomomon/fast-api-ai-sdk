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
            reasoning_stream_id = "reasoning-1"
            yield self.format_sse({"type": "start", "messageId": message_id})

            # Construct the model string expected by LiteLLM
            full_model_name = f"{self.provider_name}/{model}"
            
            reasoning_effort = None
            if litellm.supports_reasoning(model=full_model_name):
                if "/responses/" in full_model_name:
                    reasoning_effort = {"effort": "low", "summary": "detailed"}
                else:
                    reasoning_effort = "low"

            while True:
                tool_calls_state: dict[int, dict[str, Any]] = {}
                text_started = False
                reasoning_started = False
                finish_reason = None
                current_text_content = ""

                stream = await litellm.acompletion(
                    model=full_model_name,
                    messages=openai_messages,
                    stream=True,
                    tools=tool_definitions if tool_definitions else None,
                    reasoning_effort=reasoning_effort
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

                    # Handle reasoning content
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
                        current_text_content += delta.content
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
                                        "type": "tool-input-start",
                                        "toolCallId": state["id"],
                                        "toolName": state["name"],
                                    }
                                )
                                state["started"] = True
                            
                            if state["started"] and tool_call_delta.function and tool_call_delta.function.arguments:
                                yield self.format_sse(
                                    {
                                        "type": "tool-input-delta",
                                        "toolCallId": state["id"],
                                        "inputTextDelta": tool_call_delta.function.arguments,
                                    }
                                )

                # If no tool calls were collected, we are done
                if not tool_calls_state:
                    break

                # If we have tool calls, process them and continue the loop
                assistant_message_tool_calls = []
                tool_results_messages = []
                
                for index, state in tool_calls_state.items():
                    tool_call_id = state["id"]
                    tool_name = state["name"]
                    arguments_str = state["arguments"]
                    
                    try:
                        arguments = json.loads(arguments_str)

                        # Reconstruct the tool call object for the assistant message
                        assistant_message_tool_calls.append({
                            "id": tool_call_id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": arguments_str
                            }
                        })

                        yield self.format_sse(
                            {
                                "type": "tool-input-available",
                                "toolCallId": tool_call_id,
                                "toolName": tool_name,
                                "input": arguments,
                            }
                        )
                        
                        tool_func = available_tools.get(tool_name)
                        tool_result = None
                        
                        if tool_func:
                            tool_result = tool_func(**arguments)
                            yield self.format_sse(
                                {
                                    "type": "tool-output-available",
                                    "toolCallId": tool_call_id,
                                    "output": tool_result,
                                }
                            )
                        else:
                            tool_result = {"error": f"Tool {tool_name} not found"}
                            yield self.format_sse(
                                {
                                    "type": "tool-output-available",
                                    "toolCallId": tool_call_id,
                                    "output": tool_result,
                                }
                            )
                        
                        tool_results_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "name": tool_name,
                            "content": json.dumps(tool_result) if not isinstance(tool_result, str) else tool_result
                        })

                    except json.JSONDecodeError:
                        yield self.format_sse(
                            {
                                "type": "tool-output-available",
                                "toolCallId": tool_call_id,
                                "output": {"error": "Failed to parse arguments"},
                            }
                        )
                
                # Append assistant message with ALL tool calls
                openai_messages.append({
                    "role": "assistant",
                    "content": current_text_content if current_text_content else None,
                    "tool_calls": assistant_message_tool_calls
                })

                # Append tool results
                openai_messages.extend(tool_results_messages)

            yield self.format_sse({"type": "finish", "finishReason": finish_reason})

        except Exception as e:
            print(f"Error in stream_chat: {e}")
            yield self.format_sse({"type": "error", "error": str(e)})
