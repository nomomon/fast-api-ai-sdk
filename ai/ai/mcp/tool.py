"""MCPToolWrapper: wraps a single MCP server tool as a native Tool."""

import asyncio
import logging
from typing import Any

from mcp import ClientSession
from mcp.types import TextContent

from ai.agent.tools.base import Tool

logger = logging.getLogger(__name__)


class MCPToolWrapper(Tool):
    """Wraps a single MCP server tool as a native Tool."""

    def __init__(
        self,
        session: ClientSession,
        server_name: str,
        tool_def: Any,
        timeout: int = 30,
    ) -> None:
        self.name = f"mcp__{server_name}__{tool_def.name}"  # type: ignore[misc]
        self.description = tool_def.description or tool_def.name  # type: ignore[misc]
        self._session = session
        self._original_name = tool_def.name
        self._input_schema: dict[str, Any] = tool_def.inputSchema or {}
        self._timeout = timeout

    async def execute(self, input: Any) -> str:
        """Call the MCP tool with the given arguments dict."""
        try:
            result = await asyncio.wait_for(
                self._session.call_tool(self._original_name, arguments=input),
                timeout=self._timeout,
            )
        except asyncio.TimeoutError:
            logger.warning("MCP tool '%s' timed out after %ds", self.name, self._timeout)
            return f"(MCP tool call timed out after {self._timeout}s)"

        is_error = getattr(result, "is_error", None) or getattr(result, "isError", False)
        if is_error:
            return f"(error) {getattr(result, 'content', 'Tool call failed')}"

        content = getattr(result, "content", None) or []
        for block in content:
            if isinstance(block, TextContent):
                return block.text
        parts = [block.text for block in content if hasattr(block, "text")]
        if parts:
            return "\n".join(parts)

        structured = getattr(result, "structured_content", None) or getattr(
            result, "structuredContent", None
        )
        if structured is not None:
            return str(structured)

        return "(no output)"

    async def call(self, args: dict[str, Any]) -> str:
        """Pass args dict directly to execute (schema is dynamic, no Pydantic Input model)."""
        return await self.execute(args)

    def to_schema(self) -> dict[str, Any]:
        """Return OpenAI function-calling schema derived from the MCP tool definition."""
        schema = dict(self._input_schema)
        if "type" not in schema:
            schema["type"] = "object"
        if "properties" not in schema:
            schema["properties"] = {}
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": schema,
            },
        }
