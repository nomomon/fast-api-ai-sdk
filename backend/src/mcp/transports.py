"""MCP transport registry: create ClientSession from config by transport type."""

from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any

from mcp.client.stdio import StdioServerParameters, stdio_client

from mcp import ClientSession

# Factory: (config: dict) -> AbstractAsyncContextManager[ClientSession]
McpTransportFactory = Callable[[dict[str, Any]], Any]


@asynccontextmanager
async def _stdio_session(config: dict[str, Any]) -> AsyncGenerator[ClientSession, None]:
    """Create MCP session for stdio transport."""
    params = StdioServerParameters(
        command=config["command"],
        args=config.get("args") or [],
        env=config.get("env"),
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


@asynccontextmanager
async def _streamable_http_session(
    config: dict[str, Any],
) -> AsyncGenerator[ClientSession, None]:
    """Create MCP session for streamable-http transport."""
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


TRANSPORT_REGISTRY: dict[str, McpTransportFactory] = {
    "stdio": _stdio_session,
    "streamable-http": _streamable_http_session,
}


@asynccontextmanager
async def mcp_session_context(
    config: dict[str, Any],
) -> AsyncGenerator[ClientSession, None]:
    """Create MCP session from config using registered transport. Yields ClientSession."""
    transport = config.get("transport", "")
    factory = TRANSPORT_REGISTRY.get(transport)
    if factory is None:
        raise ValueError(f"Unsupported MCP transport: {transport}")
    async with factory(config) as session:
        yield session
