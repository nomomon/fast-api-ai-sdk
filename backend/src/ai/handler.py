"""Agent loop runner."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any
from uuid import UUID

from ai.agent.context import SystemPrompt
from ai.agent.events import AgentEvent
from ai.agent.loop import AgentLoop
from ai.agent.skills import FileSkillSource, SkillsLoader
from ai.agent.tools.base import Tool
from ai.agent.tools.weather import GetCurrentWeather
from ai.providers.litellm import LiteLLMProvider
from sqlalchemy.orm import Session

from ai.mcp import mcp_tools_context
from src.ai.mcp.repository import UserMcpRepository
from src.ai.prompts.repository import PromptRepository
from src.ai.skills.repository import DBSkillSource, UserSkillRepository
from src.ai.tools import LoadSkillTool, UpdateSkillTool

_prompt_repo = PromptRepository()


async def run_agent(
    messages: list[dict[str, Any]],
    model: str,
    user_id: UUID | None = None,
    db: Session | None = None,
    prompt_id: str | None = None,
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

    prompt_content = _prompt_repo.get_content_by_id(prompt_id) if prompt_id else None
    system = SystemPrompt(base=prompt_content).add_section("Skills", loader.build_summary_xml())

    provider = LiteLLMProvider()
    async with mcp_tools_context(mcp_configs) as mcp_tools:
        loop = AgentLoop(
            provider=provider,
            tools=tools + mcp_tools,
            model=model,
            system=system,
        )
        async for event in loop.run(messages):
            yield event
