"""MCP domain: user MCP configs, router, client."""

from src.mcp.router import router
from src.mcp.service import McpService

__all__ = ["router", "McpService"]
