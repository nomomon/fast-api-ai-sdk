"""Prompt schemas for API requests and responses."""

from pydantic import BaseModel


class Prompt(BaseModel):
    """Prompt schema."""

    id: str | None
    name: str
    content: str | None = None


class PromptListResponse(BaseModel):
    """Prompt list response schema."""

    prompts: list[Prompt]
