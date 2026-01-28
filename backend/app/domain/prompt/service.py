"""Prompt service for business logic."""

from app.domain.prompt.repository import PromptRepository
from app.domain.prompt.schemas import Prompt, PromptListResponse


class PromptService:
    """Service for prompt business logic."""

    def __init__(self):
        """Initialize service with repository."""
        self.repository = PromptRepository()

    def get_all(self) -> PromptListResponse:
        """Get all prompts.

        Returns:
            PromptListResponse with list of prompts
        """
        prompts_data = self.repository.get_all()
        prompts = [Prompt(**prompt) for prompt in prompts_data]
        return PromptListResponse(prompts=prompts)

    def get_by_id(self, prompt_id: str) -> str | None:
        """Get prompt content by ID.

        Args:
            prompt_id: Prompt ID

        Returns:
            Prompt content string or None if not found
        """
        return self.repository.get_content_by_id(prompt_id)
