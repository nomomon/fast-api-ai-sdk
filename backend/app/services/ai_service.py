import os
from collections.abc import AsyncGenerator

import litellm

from app.config import settings


class AIService:
    """Service for interacting with AI models."""

    def __init__(self):
        self.model = settings.openai_model
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key

    async def stream_chat(
        self, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses using LiteLLM.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Yields:
            Chunks of the response as strings
        """
        stream = await litellm.acompletion(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def chat(
        self, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000
    ) -> str:
        """
        Get a complete chat response using LiteLLM.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Complete response string
        """
        response = await litellm.acompletion(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content


# Singleton instance
ai_service = AIService()
