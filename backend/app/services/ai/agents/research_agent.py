"""Research agent implementation.

Fictional workflow: search X websites → search more → more searches →
status "generating concise response" → LLM streams text.
"""

import asyncio
import logging
import os
import random
from collections.abc import AsyncGenerator, Sequence
from typing import Any

import litellm

from app.core.config import settings
from app.services.ai.adapters.messages import ClientMessage, convert_to_openai_messages
from app.services.ai.adapters.streaming import StreamEvent
from app.services.ai.agents.base import BaseAgent
from app.services.ai.streaming.processor import StreamChunkProcessor
from app.services.ai.streaming.state import TEXT_STREAM_ID, StreamStateData

logger = logging.getLogger(__name__)

_SAMPLE_DOMAINS = (
    "example.com",
    "wikipedia.org",
    "github.com",
    "stackoverflow.com",
    "arxiv.org",
    "nature.com",
    "pubmed.ncbi.nlm.nih.gov",
    "scholar.google.com",
    "medium.com",
    "substack.com",
)


def _generate_websites(count: int | None = None) -> list[str]:
    """Generate a random list of website URLs for search data events."""
    n = count or random.randint(2, 8)
    domains = random.sample(_SAMPLE_DOMAINS, min(n, len(_SAMPLE_DOMAINS)))
    return [f"https://www.{d}" for d in domains]


class ResearchAgent(BaseAgent):
    """Research agent: emits process data parts, then streams LLM text response."""

    def __init__(self, model_id: str):
        """Initialize the research agent.

        Args:
            model_id: The model identifier (e.g., 'openai/gpt-4', 'gemini/gemini-pro')
        """
        self.model_id = model_id
        self._processor = StreamChunkProcessor()
        self._setup_environment()

    def _setup_environment(self) -> None:
        """Set up environment variables for LiteLLM."""
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        if settings.gemini_api_key:
            os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

    async def _process_text_stream(
        self,
        stream: AsyncGenerator[Any, None],
        stream_state: StreamStateData,
        text_stream_id: str,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Process only text chunks from the LLM stream (no reasoning, tools, content_parts)."""
        async for chunk in stream:
            if not chunk.choices:
                continue

            choice = chunk.choices[0]

            if choice.finish_reason is not None:
                stream_state.finish_reason = choice.finish_reason

            delta = choice.delta
            if delta is None:
                continue

            async for event in self._processor._process_text_chunk(
                delta, stream_state, text_stream_id
            ):
                yield event

    async def execute(self, messages: Sequence[ClientMessage]) -> AsyncGenerator[StreamEvent, None]:
        """Execute the research agent workflow.

        Flow: start -> N search rounds (websites) -> status "generating" ->
        stream text -> finish. No tools, no reasoning effort.

        Args:
            messages: Sequence of client messages

        Yields:
            Stream events (dicts) representing the research flow
        """
        openai_messages = convert_to_openai_messages(messages)
        stream_state = StreamStateData()
        text_stream_id = TEXT_STREAM_ID

        try:
            message_id = self._processor.generate_id()

            yield {"type": "start", "messageId": message_id}

            # 1. Emit multiple search rounds (websites found per round)
            num_rounds = random.randint(3, 6)
            for round_num in range(1, num_rounds + 1):
                websites = _generate_websites()
                async for event in self._processor._process_data_part(
                    type_suffix="search",
                    data={
                        "websites": websites,
                        "round": round_num,
                        "query": f"research round {round_num}" if round_num <= 2 else None,
                        "status": "complete",
                    },
                ):
                    yield event
                await asyncio.sleep(random.uniform(0.5, 2))

            # 2. Emit status: generating concise response
            async for event in self._processor._process_data_part(
                type_suffix="status",
                data={
                    "message": "Generating concise response...",
                    "phase": "generating",
                },
            ):
                yield event
            await asyncio.sleep(0.3)

            # 3. Stream LLM text response (no tools, no reasoning_effort)
            stream = await litellm.acompletion(
                model=self.model_id,
                messages=openai_messages,
                stream=True,
            )

            async for event in self._process_text_stream(stream, stream_state, text_stream_id):
                yield event

            yield {"type": "finish", "finishReason": stream_state.finish_reason}

        except Exception as e:
            logger.error(f"Error in research agent execution: {e}", exc_info=True)
            yield {"type": "error", "error": str(e)}
