"""MCP API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai.mcp import mcp_session_context
from src.ai.mcp._errors import format_mcp_error
from src.auth.dependencies import get_current_user
from src.database import get_db
from src.user.models import User

from .repository import UserMcpRepository
from .schemas import McpCreate, McpResponse, McpUpdate, validate_mcp_config

router = APIRouter(prefix="/mcps", tags=["mcps"])


class McpCheckResponse(BaseModel):
    """Response from MCP check/probe."""

    status: str  # "ok" | "error"
    tool_count: int
    error: str | None = None


@router.get("", response_model=list[McpResponse])
async def list_mcps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List current user's MCPs."""
    repo = UserMcpRepository(db)
    rows = repo.list_by_user(current_user.id)
    return [McpResponse.model_validate(r) for r in rows]


@router.get("/{mcp_id}", response_model=McpResponse)
async def get_mcp(
    mcp_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get one MCP by id."""
    repo = UserMcpRepository(db)
    row = repo.get_by_id(mcp_id, current_user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")
    return McpResponse.model_validate(row)


@router.post("", response_model=McpResponse, status_code=status.HTTP_201_CREATED)
async def create_mcp(
    body: McpCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new MCP config."""
    try:
        config = validate_mcp_config(body.config)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    repo = UserMcpRepository(db)
    row = repo.create(current_user.id, body.name, config)
    return McpResponse.model_validate(row)


@router.put("/{mcp_id}", response_model=McpResponse)
async def update_mcp(
    mcp_id: UUID,
    body: McpUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update MCP name and/or config."""
    config = body.config
    if config is not None:
        try:
            config = validate_mcp_config(config)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    repo = UserMcpRepository(db)
    row = repo.update(mcp_id, current_user.id, name=body.name, config=config)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")
    return McpResponse.model_validate(row)


@router.delete("/{mcp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp(
    mcp_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an MCP config."""
    repo = UserMcpRepository(db)
    if not repo.delete(mcp_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")


@router.post("/{mcp_id}/check", response_model=McpCheckResponse)
async def check_mcp(
    mcp_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Connect to MCP, list tools, update cached status and tool count, return result."""
    repo = UserMcpRepository(db)
    row = repo.get_by_id(mcp_id, current_user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")
    try:
        async with mcp_session_context(row.config) as session:
            list_result = await session.list_tools()
            tool_count = len(list_result.tools)
        repo.update_status(mcp_id, current_user.id, "ok", tool_count)
        return McpCheckResponse(status="ok", tool_count=tool_count)
    except Exception as e:
        repo.update_status(mcp_id, current_user.id, "error", None)
        return McpCheckResponse(status="error", tool_count=0, error=format_mcp_error(e))
