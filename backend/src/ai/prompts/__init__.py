"""Prompt domain package."""

from .route import router
from .schemas import Prompt, PromptListResponse

__all__ = [
    "router",
    "Prompt",
    "PromptListResponse",
]
