"""MCP config schemas and validation."""

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
    api_key: str | None = None
    headers: dict[str, str] | None = None


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
