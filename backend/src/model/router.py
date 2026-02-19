"""Models API endpoints."""

from fastapi import APIRouter

from src.model.repository import ModelRepository
from src.model.schemas import Model, ModelListResponse

router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
async def list_models():
    """List available AI models."""
    repo = ModelRepository()
    models = [Model(**m) for m in repo.get_all()]
    return ModelListResponse(models=models).model_dump()
