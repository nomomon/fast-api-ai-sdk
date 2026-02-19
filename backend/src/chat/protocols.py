"""Chat domain protocols for dependency inversion (testability)."""

from typing import Protocol
from uuid import UUID


class McpConfigProvider(Protocol):
    """Protocol for providing user MCP configs. Satisfied by UserMcpRepository adapter."""

    def list_configs(self, user_id: UUID) -> list[tuple[str, dict]]: ...
