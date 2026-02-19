"""MCP client: orchestrate sessions, merge tools with defaults."""

import logging
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

from mcp import ClientSession
from src.mcp.converters import call_tool_result_to_message, mcp_tools_to_openai
from src.mcp.transports import mcp_session_context

logger = logging.getLogger(__name__)


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
