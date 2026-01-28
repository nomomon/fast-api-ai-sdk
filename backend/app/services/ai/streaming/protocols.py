"""Protocol definitions for LLM stream delta objects."""

from typing import Protocol


class DeltaContent(Protocol):
    """Protocol for delta content objects from LLM streams."""

    content: str | None
    reasoning_content: str | None


class ToolCallDelta(Protocol):
    """Protocol for tool call delta objects from LLM streams."""

    index: int
    id: str | None

    @property
    def function(self) -> "ToolCallFunctionDelta | None":
        """Get the function delta object."""
        ...


class ToolCallFunctionDelta(Protocol):
    """Protocol for tool call function delta objects."""

    name: str | None
    arguments: str | None
