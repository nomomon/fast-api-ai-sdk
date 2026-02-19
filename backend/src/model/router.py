"""Models API endpoints."""

from fastapi import APIRouter

from src.model.service import ModelService

router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
async def list_models():
    """List available AI models."""
    model_service = ModelService()
    return model_service.get_all().model_dump()
