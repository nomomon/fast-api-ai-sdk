"""Agent loop: stream LLM responses, execute tool calls, repeat."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any

from ai.agent import context
from ai.agent.events import (
    AgentEvent,
    Error,
    Finish,
    TextDelta,
    TextStart,
    ToolInputAvailable,
    ToolInputDelta,
    ToolInputStart,
    ToolOutputAvailable,
)
from ai.agent.tools.base import Tool
from ai.providers.base import LLMProvider


class AgentLoop:
    """Streams LLM responses and executes tool calls until the model is done.

    Usage::

        loop = AgentLoop(provider=my_provider, tools=[MyTool()], model="gpt-4o")
        async for event in loop.run(messages):
            ...  # handle AgentEvent instances
    """

    def __init__(
        self,
        provider: LLMProvider,
        tools: list[Tool],
        model: str,
        system: str | None = None,
        max_iterations: int = 10,
    ) -> None:
        self.provider = provider
        self.model = model
        self.system = system
        self.max_iterations = max_iterations
        self._tools: dict[str, Tool] = {t.name: t for t in tools}

    async def run(
        self,
        messages: list[dict[str, Any]],
    ) -> AsyncGenerator[AgentEvent, None]:
        """Run the agent loop, yielding typed events as they are produced.

        Args:
            messages: Conversation history in OpenAI format.

        Yields:
            Typed AgentEvent instances (TextDelta, ToolInputDelta, Finish, …).
        """
        tool_schemas = [t.to_schema() for t in self._tools.values()]
        msgs = context.build_messages(self.system, messages)

        for _ in range(self.max_iterations):
            text_started = False
            text_content = ""

            # tool_calls_state: index → {id, name, arguments}
            tool_calls_state: dict[int, dict[str, Any]] = {}

            finish_reason: str | None = None

            async for chunk in self.provider.stream(msgs, tool_schemas, self.model):
                if chunk.finish_reason:
                    finish_reason = chunk.finish_reason

                if chunk.content:
                    if not text_started:
                        yield TextStart()
                        text_started = True
                    text_content += chunk.content
                    yield TextDelta(delta=chunk.content)

                for tc in chunk.tool_calls:
                    state = tool_calls_state.setdefault(
                        tc.index,
                        {"id": None, "name": None, "arguments": "", "started": False},
                    )
                    if tc.id:
                        state["id"] = tc.id
                    if tc.name:
                        state["name"] = tc.name
                    if tc.arguments:
                        state["arguments"] += tc.arguments

                    if state["id"] and state["name"] and not state["started"]:
                        yield ToolInputStart(
                            tool_call_id=state["id"],
                            tool_name=state["name"],
                        )
                        state["started"] = True

                    if state["started"] and tc.arguments:
                        yield ToolInputDelta(
                            tool_call_id=state["id"],
                            input_text_delta=tc.arguments,
                        )

            if not tool_calls_state:
                yield Finish(finish_reason=finish_reason or "stop")
                return

            # Execute tool calls and collect results
            assistant_tool_calls: list[dict[str, Any]] = []
            tool_result_messages: list[dict[str, Any]] = []

            for state in tool_calls_state.values():
                tool_call_id = state["id"]
                tool_name = state["name"]
                arguments_str = state["arguments"]

                if not tool_call_id:
                    continue

                try:
                    arguments = json.loads(arguments_str)
                except json.JSONDecodeError:
                    arguments = {}

                assistant_tool_calls.append({
                    "id": tool_call_id,
                    "type": "function",
                    "function": {"name": tool_name, "arguments": arguments_str},
                })

                yield ToolInputAvailable(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    input=arguments,
                )

                tool = self._tools.get(tool_name)
                if tool:
                    result = await tool.call(arguments)
                else:
                    result = f"Tool '{tool_name}' not found."

                yield ToolOutputAvailable(tool_call_id=tool_call_id, output=result)

                tool_result_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": result,
                })

            context.add_assistant_turn(msgs, text_content or None, assistant_tool_calls)
            context.add_tool_results(msgs, tool_result_messages)

        yield Error(error=f"Reached maximum iterations ({self.max_iterations}) without finishing.")
