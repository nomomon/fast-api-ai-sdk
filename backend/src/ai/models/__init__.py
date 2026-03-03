"""AI model catalog package."""

from src.ai.models.router import router
from src.ai.models.schemas import Model, ModelListResponse

__all__ = [
    "router",
    "Model",
    "ModelListResponse",
]
