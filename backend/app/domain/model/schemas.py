"""Model schemas for API requests and responses."""

from pydantic import BaseModel


class Model(BaseModel):
    """AI model schema."""

    id: str
    name: str
    provider: str


class ModelListResponse(BaseModel):
    """Model list response schema."""

    models: list[Model]
