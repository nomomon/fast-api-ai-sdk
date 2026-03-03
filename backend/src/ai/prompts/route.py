"""Prompts API endpoints."""

from fastapi import APIRouter

from .repository import PromptRepository
from .schemas import Prompt, PromptListResponse

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("")
async def list_prompts():
    """List available system prompts."""
    repo = PromptRepository()
    prompts = [Prompt(**p) for p in repo.get_all()]
    return PromptListResponse(prompts=prompts).model_dump()
