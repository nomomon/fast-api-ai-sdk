"""Prompts API endpoints."""

from fastapi import APIRouter

from src.prompt.repository import PromptRepository
from src.prompt.schemas import Prompt, PromptListResponse

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("")
async def list_prompts():
    """List available system prompts."""
    repo = PromptRepository()
    prompts = [Prompt(**p) for p in repo.get_all()]
    return PromptListResponse(prompts=prompts).model_dump()
