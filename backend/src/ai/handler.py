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

from ai.mcp import mcp_tools_context
from src.ai.mcp.repository import UserMcpRepository
from src.ai.skills.repository import DBSkillSource, UserSkillRepository
from src.ai.tools import LoadSkillTool, UpdateSkillTool


async def run_agent(
    messages: list[dict[str, Any]],
    model: str,
    user_id: UUID | None = None,
    db: Session | None = None,
) -> AsyncGenerator[AgentEvent, None]:
    skill_sources = [FileSkillSource()]
    extra_tools: list[Tool] = []
    mcp_configs: list[tuple[str, dict]] = []

    if db and user_id:
        user_skill_repo = UserSkillRepository(db)
        skill_sources.insert(0, DBSkillSource(user_skill_repo, user_id))
        extra_tools.append(UpdateSkillTool(user_skill_repo, user_id))
        mcp_configs = UserMcpRepository(db).list_configs(user_id)

    loader = SkillsLoader(skill_sources)
    tools: list[Tool] = [GetCurrentWeather(), LoadSkillTool(loader), *extra_tools]

    provider = LiteLLMProvider()
    async with mcp_tools_context(mcp_configs) as mcp_tools:
        loop = AgentLoop(
            provider=provider,
            tools=tools + mcp_tools,
            model=model,
            system=loader.build_summary_xml(),
        )
        async for event in loop.run(messages):
            yield event
