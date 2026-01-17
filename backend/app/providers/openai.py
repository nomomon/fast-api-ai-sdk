import json
import traceback
from collections.abc import Sequence
from typing import Any

from openai import OpenAI

from app.config import settings
from app.providers.base import BaseProvider
from app.utils.prompt import ClientMessage, convert_to_openai_messages
from app.utils.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str = None, base_url: str = None):
        self.client = OpenAI(api_key=api_key or settings.openai_api_key, base_url=base_url)

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
            text_finished = False
            reasoning_stream_id = "reasoning-1"
            reasoning_started = False
            reasoning_finished = False
            finish_reason = None
            usage_data = None
            tool_calls_state: dict[int, dict[str, Any]] = {}

            yield self.format_sse({"type": "start", "messageId": message_id})

            stream = self.client.chat.completions.create(
                messages=openai_messages,
                model=model,
                stream=True,
                tools=tool_definitions if tool_definitions else None,
            )

            for chunk in stream:
                for choice in chunk.choices:
                    if choice.finish_reason is not None:
                        finish_reason = choice.finish_reason

                    delta = choice.delta
                    if delta is None:
                        continue

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

                            function_call = getattr(tool_call_delta, "function", None)
                            if function_call is not None:
                                if function_call.name is not None:
                                    state["name"] = function_call.name
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

                                if function_call.arguments:
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

                                    state["arguments"] += function_call.arguments
                                    if state["id"] is not None:
                                        yield self.format_sse(
                                            {
                                                "type": "tool-input-delta",
                                                "toolCallId": state["id"],
                                                "inputTextDelta": function_call.arguments,
                                            }
                                        )

                if not chunk.choices and chunk.usage is not None:
                    usage_data = chunk.usage

            if reasoning_started and not reasoning_finished:
                yield self.format_sse({"type": "reasoning-end", "id": reasoning_stream_id})
                reasoning_finished = True

            if finish_reason == "stop" and text_started and not text_finished:
                yield self.format_sse({"type": "text-end", "id": text_stream_id})
                text_finished = True

            if finish_reason == "tool_calls":
                for index in sorted(tool_calls_state.keys()):
                    state = tool_calls_state[index]
                    tool_call_id = state.get("id")
                    tool_name = state.get("name")

                    if tool_call_id is None or tool_name is None:
                        continue

                    if not state["started"]:
                        yield self.format_sse(
                            {
                                "type": "tool-input-start",
                                "toolCallId": tool_call_id,
                                "toolName": tool_name,
                            }
                        )
                        state["started"] = True

                    raw_arguments = state["arguments"]
                    try:
                        parsed_arguments = json.loads(raw_arguments) if raw_arguments else {}
                    except Exception as error:
                        yield self.format_sse(
                            {
                                "type": "tool-input-error",
                                "toolCallId": tool_call_id,
                                "toolName": tool_name,
                                "input": raw_arguments,
                                "errorText": str(error),
                            }
                        )
                        continue

                    yield self.format_sse(
                        {
                            "type": "tool-input-available",
                            "toolCallId": tool_call_id,
                            "toolName": tool_name,
                            "input": parsed_arguments,
                        }
                    )

                    tool_function = available_tools.get(tool_name)
                    if tool_function is None:
                        yield self.format_sse(
                            {
                                "type": "tool-output-error",
                                "toolCallId": tool_call_id,
                                "errorText": f"Tool '{tool_name}' not found.",
                            }
                        )
                        continue

                    try:
                        tool_result = tool_function(**parsed_arguments)
                    except Exception as error:
                        yield self.format_sse(
                            {
                                "type": "tool-output-error",
                                "toolCallId": tool_call_id,
                                "errorText": str(error),
                            }
                        )
                    else:
                        yield self.format_sse(
                            {
                                "type": "tool-output-available",
                                "toolCallId": tool_call_id,
                                "output": tool_result,
                            }
                        )

            if text_started and not text_finished:
                yield self.format_sse({"type": "text-end", "id": text_stream_id})
                text_finished = True

            finish_metadata: dict[str, Any] = {}
            if finish_reason is not None:
                finish_metadata["finishReason"] = finish_reason.replace("_", "-")

            if usage_data is not None:
                usage_payload = {
                    "promptTokens": usage_data.prompt_tokens,
                    "completionTokens": usage_data.completion_tokens,
                }
                total_tokens = getattr(usage_data, "total_tokens", None)
                if total_tokens is not None:
                    usage_payload["totalTokens"] = total_tokens
                finish_metadata["usage"] = usage_payload

            if finish_metadata:
                yield self.format_sse({"type": "finish", "messageMetadata": finish_metadata})
            else:
                yield self.format_sse({"type": "finish"})

            yield "data: [DONE]\n\n"
        except Exception:
            traceback.print_exc()
            yield self.format_sse({"type": "error", "text": "An error occurred during streaming."})
