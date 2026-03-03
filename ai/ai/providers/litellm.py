"""LiteLLM provider implementation."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import litellm

from ai.providers.base import ChunkDelta, LLMProvider, ToolCallDelta


class LiteLLMProvider(LLMProvider):
    """LLM provider backed by LiteLLM, supporting OpenAI, Anthropic, Gemini, and more.

    Usage::

        provider = LiteLLMProvider()
        async for chunk in provider.stream(messages, tools, model="gpt-4o"):
            ...
    """

    async def stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        model: str,
    ) -> AsyncGenerator[ChunkDelta, None]:
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "tools": tools or None,  # some providers reject an empty list
            "stream": True,
        }

        response = await litellm.acompletion(**kwargs)

        async for chunk in response:
            if not chunk.choices:
                continue

            choice = chunk.choices[0]
            delta = choice.delta

            tool_call_deltas: list[ToolCallDelta] = []
            for tc in delta.tool_calls or []:
                tool_call_deltas.append(
                    ToolCallDelta(
                        index=tc.index,
                        id=tc.id,
                        name=tc.function.name if tc.function else None,
                        arguments=tc.function.arguments or "" if tc.function else "",
                    )
                )

            yield ChunkDelta(
                content=delta.content,
                tool_calls=tool_call_deltas,
                finish_reason=choice.finish_reason,
            )
