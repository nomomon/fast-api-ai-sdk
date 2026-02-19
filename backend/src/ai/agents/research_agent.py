"""Research agent implementation."""

import asyncio
import logging
import os
import random
from collections.abc import AsyncGenerator, Sequence
from typing import Any

import litellm

from src.ai.adapters.messages import ClientMessage, convert_to_openai_messages
from src.ai.adapters.streaming import StreamEvent
from src.ai.agents.base import BaseAgent
from src.ai.streaming.processor import StreamChunkProcessor
from src.ai.streaming.state import TEXT_STREAM_ID, StreamStateData
from src.config import settings

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

_SAMPLE_LABELS = (
    "Looking up on the web...",
    "Digging deeper...",
    "I'm not sure if this is a good idea, but I'm gonna do it anyway...",
    "Brainstorming...",
    "Lemme look up some memes while I'm at it...",
    "Doing some research...",
    "I'm really not sure about this one...",
)


def _generate_websites(count: int | None = None) -> list[str]:
    """Generate a random list of website URLs for search data events."""
    n = count or random.randint(2, 8)
    domains = random.sample(_SAMPLE_DOMAINS, min(n, len(_SAMPLE_DOMAINS)))
    return [f"https://www.{d}" for d in domains]


class ResearchAgent(BaseAgent):
    """Research agent: emits process data parts, then streams LLM text response."""

    def __init__(self, model_id: str):
        """Initialize the research agent."""
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
        """Process only text chunks from the LLM stream."""
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
        """Execute the research agent workflow."""
        openai_messages = convert_to_openai_messages(messages)
        stream_state = StreamStateData()
        text_stream_id = TEXT_STREAM_ID

        try:
            message_id = self._processor.generate_id()

            yield {"type": "start", "messageId": message_id}

            async for event in self._processor._process_data_part(
                type_suffix="start-label",
                data={"label": "Researching..."},
            ):
                yield event

            num_rounds = random.randint(3, 6)
            for _ in range(1, num_rounds + 1):
                websites = _generate_websites()
                details = [u.split("//")[-1].split("/")[0] for u in websites]
                async for event in self._processor._process_data_part(
                    type_suffix="step",
                    data={
                        "label": random.choice(_SAMPLE_LABELS),
                        "details": details,
                        "type": "search",
                    },
                ):
                    yield event
                await asyncio.sleep(random.uniform(0.5, 2))

            async for event in self._processor._process_data_part(
                type_suffix="step",
                data={"label": "Summarizing the information...", "type": "status"},
            ):
                yield event
            await asyncio.sleep(0.3)

            async for event in self._processor._process_data_part(
                type_suffix="end-label",
                data={"label": "Research completed. Here is my conclusion:"},
            ):
                yield event

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
