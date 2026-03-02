"""Typed streaming events emitted by the agent loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Union


@dataclass
class TextStart:
    pass


@dataclass
class TextDelta:
    delta: str


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
class Finish:
    finish_reason: str


@dataclass
class Error:
    error: str


AgentEvent = Union[
    TextStart,
    TextDelta,
    ToolInputStart,
    ToolInputDelta,
    ToolInputAvailable,
    ToolOutputAvailable,
    Finish,
    Error,
]
