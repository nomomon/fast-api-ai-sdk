"""Tool registry: one file per tool, single definition for schema and implementation."""

import importlib
from typing import Any

from app.services.ai.tools.schema import function_to_openai_tool

# Explicit list of tool modules (one per file). Module name = tool name = function name.
_TOOL_MODULES = [
    "get_current_weather",
]


def _load_tools() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Discover tool modules, build OpenAI definitions and name-to-callable map."""
    definitions: list[dict[str, Any]] = []
    implementations: dict[str, Any] = {}

    for module_name in _TOOL_MODULES:
        mod = importlib.import_module(f"app.services.ai.tools.{module_name}")
        fn = getattr(mod, module_name, None)
        if fn is None or not callable(fn):
            continue
        definitions.append(function_to_openai_tool(module_name, fn))
        implementations[module_name] = fn

    return definitions, implementations


TOOL_DEFINITIONS, AVAILABLE_TOOLS = _load_tools()
