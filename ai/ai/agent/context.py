"""Helpers for building and updating the OpenAI-format messages list."""

from __future__ import annotations

from typing import Any

_SECTION_SEPARATOR = "\n\n---\n\n"


class SystemPrompt:
    """Composable system prompt builder.

    Start with an optional base instruction, then chain `add_section()` calls
    to append named blocks (skills summary, tool hints, etc.).  Call `build()`
    to get the final string, or pass the instance directly to `build_messages`.

    Example::

        system = (
            SystemPrompt(base="You are a concise assistant.")
            .add_section("Available Skills", skills_xml)
        )
        msgs = build_messages(system, history)
    """

    def __init__(self, base: str | None = None) -> None:
        self._base = base or ""
        self._sections: list[tuple[str, str]] = []

    def add_section(self, heading: str, content: str) -> "SystemPrompt":
        """Append a named section to the system prompt.

        Sections with empty content are silently skipped at build time.
        Returns self to allow chaining.
        """
        self._sections.append((heading, content))
        return self

    def build(self) -> str | None:
        """Assemble all parts into a single string.

        Returns None when there is nothing to render (no base, no sections
        with content), so callers can treat it the same as a missing prompt.
        """
        parts: list[str] = []
        if self._base:
            parts.append(self._base)
        for heading, content in self._sections:
            if content and content.strip():
                parts.append(f"# {heading}\n\n{content}")
        if not parts:
            return None
        return _SECTION_SEPARATOR.join(parts)


def build_messages(
    system: SystemPrompt | str | None,
    history: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return a new messages list, prepending a system message if provided."""
    if isinstance(system, SystemPrompt):
        system_str = system.build()
    else:
        system_str = system
    messages = []
    if system_str:
        messages.append({"role": "system", "content": system_str})
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
