"""Skill schemas for internal use."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


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


# API schemas for REST endpoints


class SkillCreate(BaseModel):
    """Create skill request."""

    name: str = Field(..., min_length=1, max_length=64)
    description: str = Field(default="")
    content: str = Field(default="")


class SkillUpdate(BaseModel):
    """Update skill request."""

    name: str | None = Field(None, min_length=1, max_length=64)
    description: str | None = None
    content: str | None = None


class SkillResponse(BaseModel):
    """Skill API response."""

    id: UUID
    name: str
    description: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
