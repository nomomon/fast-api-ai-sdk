"""MCP client: connect, list tools (OpenAI format), call tools."""

import logging
from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import CallToolResult, ListToolsResult, TextContent

logger = logging.getLogger(__name__)


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


@asynccontextmanager
async def mcp_session_context(config: dict[str, Any]) -> AsyncGenerator[ClientSession, None]:
    """Create MCP session from config (stdio or streamable-http). Yields ClientSession."""
    transport = config.get("transport", "")
    if transport == "stdio":
        params = StdioServerParameters(
            command=config["command"],
            args=config.get("args") or [],
            env=config.get("env"),
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                yield session
    elif transport == "streamable-http":
        import httpx

        from mcp.client.streamable_http import streamable_http_client

        url = config["url"]
        request_headers: dict[str, str] = {}
        if config.get("api_key"):
            request_headers["X-API-Key"] = config["api_key"]
        if config.get("headers"):
            request_headers.update(config["headers"])
        async with httpx.AsyncClient(headers=request_headers or None) as http_client:
            async with streamable_http_client(url, http_client=http_client) as (
                read_stream,
                write_stream,
                _,
            ):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    yield session
    else:
        raise ValueError(f"Unsupported MCP transport: {transport}")


@asynccontextmanager
async def get_user_mcp_tools_context(
    mcp_configs: list[tuple[str, dict[str, Any]]],
    default_tool_definitions: list[dict[str, Any]],
    default_available_tools: dict[str, Any],
):
    """
    Async context manager: open MCP sessions for each config, merge their tools with defaults,
    yield (tool_definitions, available_tools). On exit, close all sessions.
    """
    stack = AsyncExitStack()
    sessions: list[ClientSession] = []
    try:
        for _name, cfg in mcp_configs:
            try:
                cm = mcp_session_context(cfg)
                session = await stack.enter_async_context(cm)
                sessions.append(session)
            except Exception as e:
                logger.warning(
                    "Skipping MCP config %s: %s", cfg.get("url") or cfg.get("command"), e
                )

        tool_definitions = list(default_tool_definitions)
        available_tools = dict(default_available_tools)
        default_names = set(available_tools.keys())

        for session in sessions:
            try:
                list_result = await session.list_tools()
                openai_tools = mcp_tools_to_openai(list_result)

                def _make_mcp_runner(sess: ClientSession, tool_name: str):
                    async def runner(**kwargs: Any) -> str | dict[str, Any]:
                        result = await sess.call_tool(tool_name, kwargs)
                        return call_tool_result_to_message(result)

                    return runner

                for t in openai_tools:
                    name = t["function"]["name"]
                    if name in default_names:
                        continue
                    default_names.add(name)
                    tool_definitions.append(t)
                    available_tools[name] = _make_mcp_runner(session, name)
            except Exception as e:
                logger.warning("Failed to list tools from MCP session: %s", e)

        yield tool_definitions, available_tools
    finally:
        await stack.aclose()
