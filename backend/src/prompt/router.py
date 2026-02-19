"""Prompts API endpoints."""

from fastapi import APIRouter

from src.prompt.service import PromptService

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("")
async def list_prompts():
    """List available system prompts."""
    prompt_service = PromptService()
    return prompt_service.get_all().model_dump()
