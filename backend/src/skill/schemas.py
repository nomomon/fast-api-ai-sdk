"""Skill schemas for internal use."""

from pydantic import BaseModel


class SkillMetadata(BaseModel):
    """Skill metadata (frontmatter only)."""

    name: str
    description: str
    path: str | None = None


class Skill(BaseModel):
    """Skill with metadata and body content."""

    name: str
    description: str
    content: str | None = None
    path: str | None = None


class SkillListResponse(BaseModel):
    """Skill list response schema."""

    skills: list[Skill]
