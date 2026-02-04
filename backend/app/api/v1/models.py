"""Models API endpoints."""

from fastapi import APIRouter

from app.domain.model.service import ModelService

router = APIRouter(tags=["models"])


@router.get("/models")
async def list_models():
    """List available AI models."""
    model_service = ModelService()
    return model_service.get_all().model_dump()
