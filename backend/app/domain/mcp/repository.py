"""MCP repository for data access."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.mcp.models import UserMcp


class UserMcpRepository:
    """Repository for user MCP configs."""

    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, user_id: UUID) -> list[UserMcp]:
        """Return all MCPs for the user."""
        return (
            self.db.query(UserMcp).filter(UserMcp.user_id == user_id).order_by(UserMcp.name).all()
        )

    def get_by_id(self, id: UUID, user_id: UUID) -> UserMcp | None:
        """Return MCP by id if it belongs to the user."""
        return self.db.query(UserMcp).filter(UserMcp.id == id, UserMcp.user_id == user_id).first()

    def create(self, user_id: UUID, name: str, config: dict) -> UserMcp:
        """Create a new MCP config."""
        row = UserMcp(user_id=user_id, name=name, config=config)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def update(
        self, id: UUID, user_id: UUID, name: str | None = None, config: dict | None = None
    ) -> UserMcp | None:
        """Update MCP; return None if not found."""
        row = self.get_by_id(id, user_id)
        if row is None:
            return None
        if name is not None:
            row.name = name
        if config is not None:
            row.config = config
        self.db.commit()
        self.db.refresh(row)
        return row

    def update_status(
        self,
        id: UUID,
        user_id: UUID,
        last_status: str,
        last_tool_count: int | None,
    ) -> UserMcp | None:
        """Update cached status and tool count."""
        row = self.get_by_id(id, user_id)
        if row is None:
            return None
        from datetime import datetime

        row.last_status = last_status
        row.last_tool_count = last_tool_count
        row.last_checked_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete(self, id: UUID, user_id: UUID) -> bool:
        """Delete MCP; return True if deleted."""
        row = self.get_by_id(id, user_id)
        if row is None:
            return False
        self.db.delete(row)
        self.db.commit()
        return True
