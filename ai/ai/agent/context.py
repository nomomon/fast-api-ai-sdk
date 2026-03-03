"""Helpers for building and updating the OpenAI-format messages list."""

from __future__ import annotations

from typing import Any


def build_messages(
    system: str | None,
    history: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return a new messages list, prepending a system message if provided."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.extend(history)
    return messages


def add_assistant_turn(
    messages: list[dict[str, Any]],
    content: str | None,
    tool_calls: list[dict[str, Any]],
) -> None:
    """Append an assistant message with optional text content and tool calls."""
    messages.append(
        {
            "role": "assistant",
            "content": content,
            "tool_calls": tool_calls,
        }
    )


def add_tool_results(
    messages: list[dict[str, Any]],
    results: list[dict[str, Any]],
) -> None:
    """Append tool result messages (role=tool) to the messages list."""
    messages.extend(results)
