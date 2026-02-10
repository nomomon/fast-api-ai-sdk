"""MCP service for business logic."""

from uuid import UUID

from app.domain.mcp.repository import UserMcpRepository
from app.domain.mcp.schemas import McpResponse, validate_mcp_config


class McpService:
    """Service for user MCP config CRUD."""

    def __init__(self, db):
        self._repo = UserMcpRepository(db)

    def list(self, user_id: UUID) -> list[McpResponse]:
        """List all MCPs for the user."""
        rows = self._repo.list_by_user(user_id)
        return [McpResponse.model_validate(r) for r in rows]

    def get(self, id: UUID, user_id: UUID) -> McpResponse | None:
        """Get one MCP by id if it belongs to the user."""
        row = self._repo.get_by_id(id, user_id)
        return McpResponse.model_validate(row) if row else None

    def create(self, user_id: UUID, name: str, config: dict) -> McpResponse:
        """Create MCP after validating config."""
        config = validate_mcp_config(config)
        row = self._repo.create(user_id, name, config)
        return McpResponse.model_validate(row)

    def update(
        self, id: UUID, user_id: UUID, name: str | None = None, config: dict | None = None
    ) -> McpResponse | None:
        """Update MCP; validate config if provided."""
        if config is not None:
            config = validate_mcp_config(config)
        row = self._repo.update(id, user_id, name=name, config=config)
        return McpResponse.model_validate(row) if row else None

    def delete(self, id: UUID, user_id: UUID) -> bool:
        """Delete MCP; return True if deleted."""
        return self._repo.delete(id, user_id)

    def update_status(
        self, id: UUID, user_id: UUID, last_status: str, last_tool_count: int | None
    ) -> McpResponse | None:
        """Update cached status for an MCP."""
        row = self._repo.update_status(id, user_id, last_status, last_tool_count)
        return McpResponse.model_validate(row) if row else None
