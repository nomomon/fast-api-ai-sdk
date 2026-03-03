"""MCP client: open sessions and yield native Tool instances for each MCP tool."""

import logging
from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

from ai.agent.tools.base import Tool

from .tool import MCPToolWrapper
from .transports import mcp_session_context

logger = logging.getLogger(__name__)


@asynccontextmanager
async def mcp_tools_context(
    configs: list[tuple[str, dict[str, Any]]],
    timeout: int = 30,
) -> AsyncGenerator[list[Tool], None]:
    """Open MCP sessions for each config and yield a list of native Tool instances.

    Each MCP tool becomes an MCPToolWrapper that can be passed directly to AgentLoop
    alongside any other tools — no special MCP handling required by the caller.

    Failed servers are skipped with a warning so one bad config won't block the rest.
    """
    async with AsyncExitStack() as stack:
        tools: list[Tool] = []
        for server_name, cfg in configs:
            try:
                session = await stack.enter_async_context(mcp_session_context(cfg))
                list_result = await session.list_tools()
                for tool_def in list_result.tools:
                    tools.append(MCPToolWrapper(session, server_name, tool_def, timeout=timeout))
                logger.debug(
                    "MCP server '%s': connected, %d tools registered",
                    server_name,
                    len(list_result.tools),
                )
            except Exception as e:
                logger.warning(
                    "Skipping MCP server '%s' (%s): %s",
                    server_name,
                    cfg.get("url") or cfg.get("command"),
                    e,
                )
        yield tools
