"""MCP schemas for API and validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ai.mcp import McpConfig, McpConfigStdio, McpConfigStreamableHttp, validate_mcp_config

__all__ = [
    "McpConfig",
    "McpConfigStdio",
    "McpConfigStreamableHttp",
    "validate_mcp_config",
    "McpCreate",
    "McpUpdate",
    "McpResponse",
]


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
