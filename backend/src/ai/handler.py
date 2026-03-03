"""Agent loop runner."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any
from uuid import UUID

from ai.agent.events import AgentEvent
from ai.agent.loop import AgentLoop
from ai.agent.skills import FileSkillSource, SkillsLoader
from ai.agent.tools.base import Tool
from ai.agent.tools.weather import GetCurrentWeather
from ai.providers.litellm import LiteLLMProvider
from sqlalchemy.orm import Session

from src.ai.skills.repository import DBSkillSource, UserSkillRepository
from src.ai.tools import LoadSkillTool, UpdateSkillTool


async def run_agent(
    messages: list[dict[str, Any]],
    model: str,
    user_id: UUID | None = None,
    db: Session | None = None,
) -> AsyncGenerator[AgentEvent, None]:
    user_repo = UserSkillRepository(db) if db else None

    sources = []
    if user_repo and user_id:
        sources.append(DBSkillSource(user_repo, user_id))
    sources.append(FileSkillSource())
    loader = SkillsLoader(sources)

    system = loader.build_summary_xml()
    tools: list[Tool] = [GetCurrentWeather(), LoadSkillTool(loader)]
    if user_repo and user_id:
        tools.append(UpdateSkillTool(user_repo, user_id))

    provider = LiteLLMProvider()
    loop = AgentLoop(provider=provider, tools=tools, model=model, system=system)
    async for event in loop.run(messages):
        yield event
