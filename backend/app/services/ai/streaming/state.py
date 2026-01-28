"""State management for streaming conversation flow."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

# Stream ID constants
TEXT_STREAM_ID = "text-1"
REASONING_STREAM_ID = "reasoning-1"


class StreamState(Enum):
    """State machine for streaming conversation flow."""

    INITIAL = auto()
    STREAMING = auto()
    PROCESSING_TOOLS = auto()
    FINISHED = auto()
    ERROR = auto()


@dataclass
class StreamStateData:
    """Data class for tracking stream state during processing."""

    text_started: bool = False
    reasoning_started: bool = False
    finish_reason: str | None = None
    current_text_content: str = ""
    tool_calls_state: dict[int, dict[str, Any]] = field(default_factory=dict)
