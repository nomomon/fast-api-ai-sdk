"""Skill schemas for internal use."""

from datetime import datetime
from uuid import UUID

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


class UserSkillResponse(BaseModel):
    """User-owned skill for REST API (id, timestamps)."""

    id: UUID
    name: str
    description: str
    content: str
    created_at: datetime
    updated_at: datetime


class UserSkillListResponse(BaseModel):
    """List of user skills for REST API."""

    skills: list[UserSkillResponse]


class UserSkillUpdateRequest(BaseModel):
    """Request body for PATCH /skills/{id}."""

    description: str | None = None
    content: str | None = None
