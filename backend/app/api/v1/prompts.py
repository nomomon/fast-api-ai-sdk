"""Prompts API endpoints."""

from fastapi import APIRouter

from app.domain.prompt.service import PromptService

router = APIRouter(tags=["prompts"])


@router.get("/prompts")
async def list_prompts():
    """List available system prompts."""
    prompt_service = PromptService()
    return prompt_service.get_all().model_dump()
