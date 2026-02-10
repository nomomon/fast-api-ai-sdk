"""MCP schemas for API and validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class McpConfigStdio(BaseModel):
    """Config for stdio transport."""

    transport: str = "stdio"
    command: str = Field(..., min_length=1)
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)


class McpConfigStreamableHttp(BaseModel):
    """Config for streamable-http transport."""

    transport: str = "streamable-http"
    url: str = Field(..., min_length=1)


# Union type for config (stdio or streamable-http)
McpConfig = McpConfigStdio | McpConfigStreamableHttp


def validate_mcp_config(config: dict) -> dict:
    """Validate config shape; return normalized dict or raise ValueError."""
    transport = config.get("transport")
    if transport == "stdio":
        c = McpConfigStdio.model_validate(config)
        return c.model_dump()
    if transport == "streamable-http":
        c = McpConfigStreamableHttp.model_validate(config)
        return c.model_dump()
    raise ValueError("config.transport must be 'stdio' or 'streamable-http'")


class McpCreate(BaseModel):
    """Create MCP request."""

    name: str = Field(..., min_length=1, max_length=128)
    config: dict


class McpUpdate(BaseModel):
    """Update MCP request."""

    name: str | None = Field(None, min_length=1, max_length=128)
    config: dict | None = None


class McpResponse(BaseModel):
    """MCP response with optional status cache."""

    id: UUID
    name: str
    config: dict
    last_status: str | None = None
    last_tool_count: int | None = None
    last_checked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
