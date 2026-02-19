"""MCP format conversion: MCP types to OpenAI function-calling format."""

from typing import Any

from mcp.types import CallToolResult, ListToolsResult, TextContent


def _normalize_input_schema(input_schema: dict | None) -> dict:
    """Normalize MCP input schema to OpenAI function-calling format."""
    if not input_schema:
        return {"type": "object", "properties": {}, "additionalProperties": False}
    normalized = dict(input_schema)
    if "type" not in normalized:
        normalized["type"] = "object"
    if "properties" not in normalized:
        normalized["properties"] = {}
    if "additionalProperties" not in normalized:
        normalized["additionalProperties"] = False
    return normalized


def mcp_tools_to_openai(list_result: ListToolsResult) -> list[dict[str, Any]]:
    """Convert MCP ListToolsResult to list of OpenAI-format tool definitions."""
    tools: list[dict[str, Any]] = []
    for tool in list_result.tools:
        params = _normalize_input_schema(
            tool.input_schema
            if hasattr(tool, "input_schema")
            else getattr(tool, "inputSchema", None)
        )
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": params,
                },
            }
        )
    return tools


def call_tool_result_to_message(result: CallToolResult) -> str | dict[str, Any]:
    """Convert MCP CallToolResult to string or dict for chat tool result."""
    is_error = getattr(result, "is_error", None) or getattr(result, "isError", False)
    if is_error:
        return {"error": str(getattr(result, "content", "Tool call failed"))}
    # Prefer text from content
    content = getattr(result, "content", None) or []
    if content:
        for block in content:
            if isinstance(block, TextContent):
                return block.text
        parts = []
        for block in content:
            if hasattr(block, "text"):
                parts.append(block.text)
        if parts:
            return "\n".join(parts)
    # Structured content (v1 uses structuredContent)
    structured = getattr(result, "structured_content", None) or getattr(
        result, "structuredContent", None
    )
    if structured is not None:
        return structured
    return ""
