"""Schema extraction from tool functions for OpenAI/LiteLLM function calling."""

import inspect
import re
from collections.abc import Callable
from typing import Any, get_args, get_origin

# Python type to JSON Schema type mapping
_TYPE_MAP = {
    int: "integer",
    float: "number",
    str: "string",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def _parse_google_docstring(docstring: str | None) -> tuple[str, dict[str, str]]:
    """Parse Google-style docstring into summary and Args descriptions.

    Returns:
        (description, {param_name: param_description})
    """
    if not docstring or not docstring.strip():
        return "", {}

    description = ""
    args_descriptions: dict[str, str] = {}
    lines = docstring.strip().split("\n")
    in_args = False
    current_param: str | None = None
    current_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Args:"):
            in_args = True
            if not description and current_lines:
                description = " ".join(current_lines).strip()
            current_lines = []
            continue
        if stripped.startswith("Returns:") or stripped.startswith("Raises:"):
            in_args = False
            if current_param:
                args_descriptions[current_param] = " ".join(current_lines).strip()
            current_param = None
            current_lines = []
            continue
        if in_args:
            match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", stripped)
            if match:
                if current_param:
                    args_descriptions[current_param] = " ".join(current_lines).strip()
                current_param = match.group(1)
                current_lines = [match.group(2)] if match.group(2) else []
                continue
            if current_param and (stripped or current_lines):
                current_lines.append(stripped)
            continue
        if not in_args and stripped and not stripped.startswith("Args:"):
            current_lines.append(stripped)

    if current_param:
        args_descriptions[current_param] = " ".join(current_lines).strip()
    if not description and current_lines:
        description = " ".join(current_lines).strip()

    return description, args_descriptions


def _python_type_to_json_schema(annotation: Any) -> dict[str, Any]:
    """Convert a Python type annotation to JSON Schema for a single value."""
    origin = get_origin(annotation)
    args = get_args(annotation) if origin is not None else ()

    if origin is type(None) or annotation is type(None):
        return {"type": "string"}  # fallback

    # Optional[X] -> Union[X, None]
    if str(annotation).startswith("typing.Optional") or (origin is type(None)):
        # Optional: get the inner type
        for a in args or (annotation,):
            if a is not type(None):
                return _python_type_to_json_schema(a)
        return {"type": "string"}

    if origin is list or annotation is list:
        item_schema = {"type": "string"}
        if args:
            item_schema = _python_type_to_json_schema(args[0])
        return {"type": "array", "items": item_schema}

    if origin is dict or annotation is dict:
        if args and len(args) >= 2:
            return {"type": "object", "additionalProperties": _python_type_to_json_schema(args[1])}
        return {"type": "object"}

    if origin is tuple:
        return {"type": "array"}

    if annotation in _TYPE_MAP:
        return {"type": _TYPE_MAP[annotation]}

    # Handle Union (e.g. Optional) by taking first non-None
    if hasattr(annotation, "__origin__"):
        if origin is type(None):
            return {"type": "string"}
        for a in args or ():
            if a is not type(None):
                return _python_type_to_json_schema(a)

    return {"type": "string"}


def _is_optional(annotation: Any) -> bool:
    """Return True if the annotation is Optional[...] or Union[..., None]."""
    if annotation is Any or annotation is inspect.Parameter.empty:
        return False
    origin = get_origin(annotation)
    args = get_args(annotation) if origin is not None else ()
    if str(annotation).startswith("typing.Optional"):
        return True
    if origin is not None and type(None) in (args or ()):
        return True
    return False


def function_to_openai_tool(name: str, fn: Callable[..., Any]) -> dict[str, Any]:
    """Build an OpenAI-format tool definition from a callable.

    Uses the function signature and type hints for parameters, and the
    docstring (Google style) for description and parameter descriptions.

    Args:
        name: Tool name (must match function name for consistency).
        fn: The tool function (sync callable with type hints and docstring).

    Returns:
        Dict in OpenAI format for LiteLLM tools (type, function.name/description/parameters).
    """
    sig = inspect.signature(fn)
    hints = getattr(fn, "__annotations__", {}) or {}
    doc = inspect.getdoc(fn)
    description, param_descriptions = _parse_google_docstring(doc)

    properties: dict[str, Any] = {}
    required: list[str] = []

    for param_name, param in sig.parameters.items():
        if param_name == "self" or param.kind not in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            continue
        annotation = hints.get(param_name, Any)
        if annotation is inspect.Parameter.empty:
            annotation = Any

        prop = _python_type_to_json_schema(annotation)
        if param_descriptions.get(param_name):
            prop["description"] = param_descriptions[param_name]
        properties[param_name] = prop
        if not _is_optional(annotation):
            required.append(param_name)

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "required": required,
    }

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description or "",
            "parameters": parameters,
        },
    }
