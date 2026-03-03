"""Typed streaming events emitted by the agent loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Union


@dataclass
class MessageStart:
    message_id: str


@dataclass
class TextStart:
    id: str


@dataclass
class TextDelta:
    id: str
    delta: str


@dataclass
class TextEnd:
    id: str


@dataclass
class ReasoningStart:
    id: str


@dataclass
class ReasoningDelta:
    id: str
    delta: str


@dataclass
class ReasoningEnd:
    id: str


@dataclass
class SourceUrl:
    source_id: str
    url: str


@dataclass
class SourceDocument:
    source_id: str
    media_type: str
    title: str


@dataclass
class FilePart:
    url: str
    media_type: str


@dataclass
class DataPart:
    data_type: str  # used as suffix in "data-{data_type}"
    data: dict[str, Any]


@dataclass
class ToolInputStart:
    tool_call_id: str
    tool_name: str


@dataclass
class ToolInputDelta:
    tool_call_id: str
    input_text_delta: str


@dataclass
class ToolInputAvailable:
    tool_call_id: str
    tool_name: str
    input: dict[str, Any]


@dataclass
class ToolOutputAvailable:
    tool_call_id: str
    output: str


@dataclass
class StartStep:
    pass


@dataclass
class FinishStep:
    pass


@dataclass
class Finish:
    finish_reason: str = "stop"


@dataclass
class Abort:
    reason: str


@dataclass
class Error:
    error_text: str


AgentEvent = Union[
    MessageStart,
    TextStart,
    TextDelta,
    TextEnd,
    ReasoningStart,
    ReasoningDelta,
    ReasoningEnd,
    SourceUrl,
    SourceDocument,
    FilePart,
    DataPart,
    ToolInputStart,
    ToolInputDelta,
    ToolInputAvailable,
    ToolOutputAvailable,
    StartStep,
    FinishStep,
    Finish,
    Abort,
    Error,
]
