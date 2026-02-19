"""Model repository for data access."""


class ModelRepository:
    """Repository for AI model data access operations."""

    # In-memory storage; can be migrated to config/DB later
    MODELS_DATA = [
        {"id": "openai/gpt-5", "name": "GPT-5", "provider": "OpenAI"},
        {"id": "openai/responses/gpt-5", "name": "GPT-5 Think", "provider": "OpenAI"},
        {"id": "gemini/gemini-3-flash-preview", "name": "Gemini 3 Flash", "provider": "Google"},
    ]

    def get_all(self) -> list[dict]:
        """Get all models.

        Returns:
            List of model dictionaries
        """
        return list(self.MODELS_DATA)

    def get_by_id(self, model_id: str) -> dict | None:
        """Get model by ID.

        Args:
            model_id: Model ID (e.g. 'openai/gpt-5')

        Returns:
            Model dictionary or None if not found
        """
        for model in self.MODELS_DATA:
            if model["id"] == model_id:
                return model
        return None

    def exists(self, model_id: str) -> bool:
        """Check whether a model ID is allowed.

        Args:
            model_id: Model ID to check

        Returns:
            True if the model exists, False otherwise
        """
        return self.get_by_id(model_id) is not None

    def get_default_id(self) -> str:
        """Return the default model ID (first in list)."""
        if not self.MODELS_DATA:
            raise ValueError("No models configured")
        return self.MODELS_DATA[0]["id"]
