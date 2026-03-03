"""Agent loop runner."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from ai.agent.events import AgentEvent
from ai.agent.loop import AgentLoop
from ai.agent.tools.weather import GetCurrentWeather
from ai.providers.litellm import LiteLLMProvider


async def run_agent(
    messages: list[dict[str, Any]],
    model: str,
) -> AsyncGenerator[AgentEvent, None]:
    provider = LiteLLMProvider()
    loop = AgentLoop(provider=provider, tools=[GetCurrentWeather()], model=model)
    async for event in loop.run(messages):
        yield event
