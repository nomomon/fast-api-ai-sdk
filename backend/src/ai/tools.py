"""Backend-specific agent tools for skill operations."""

from __future__ import annotations

from uuid import UUID

from ai.agent.skills import SkillsLoader
from ai.agent.tools.base import Tool
from pydantic import BaseModel, Field

from src.ai.skills.repository import UserSkillRepository


class LoadSkillTool(Tool):
    """Load the content of a skill by name."""

    class Input(BaseModel):
        name: str = Field(..., description="Name of the skill to load")

    def __init__(self, loader: SkillsLoader) -> None:
        self._loader = loader

    async def execute(self, input: Input) -> str:
        content = self._loader.load_content(input.name)
        return content or f"Skill '{input.name}' not found."


class UpdateSkillTool(Tool):
    """Create or update a user skill with the given name, description, and content."""

    class Input(BaseModel):
        name: str = Field(..., description="Skill name (lowercase letters, numbers, hyphens)")
        description: str = Field(..., description="Short description of what the skill does")
        content: str = Field(..., description="Markdown body of the skill")

    def __init__(self, repo: UserSkillRepository, user_id: UUID) -> None:
        self._repo = repo
        self._user_id = user_id

    async def execute(self, input: Input) -> str:
        row = self._repo.create_or_update(
            self._user_id, input.name, input.description, input.content
        )
        return "Skill saved." if row else "Failed to save skill (name may be invalid)."
