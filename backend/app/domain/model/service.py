"""Model service for business logic."""

from app.domain.model.repository import ModelRepository
from app.domain.model.schemas import Model, ModelListResponse


class ModelService:
    """Service for AI model business logic."""

    def __init__(self):
        """Initialize service with repository."""
        self.repository = ModelRepository()

    def get_all(self) -> ModelListResponse:
        """Get all available models.

        Returns:
            ModelListResponse with list of models
        """
        models_data = self.repository.get_all()
        models = [Model(**m) for m in models_data]
        return ModelListResponse(models=models)

    def get_by_id(self, model_id: str) -> Model | None:
        """Get model by ID.

        Args:
            model_id: Model ID

        Returns:
            Model or None if not found
        """
        data = self.repository.get_by_id(model_id)
        return Model(**data) if data else None

    def is_valid_model_id(self, model_id: str) -> bool:
        """Check whether the given model ID is one of the allowed models.

        Args:
            model_id: Model ID to validate

        Returns:
            True if valid, False otherwise
        """
        return self.repository.exists(model_id)

    def get_default_model_id(self) -> str:
        """Return the default model ID."""
        return self.repository.get_default_id()
