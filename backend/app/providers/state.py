"""State management for streaming conversation flow."""

from enum import Enum, auto

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
