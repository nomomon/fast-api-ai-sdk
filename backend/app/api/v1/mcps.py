"""MCP API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.domain.mcp.schemas import McpCreate, McpResponse, McpUpdate
from app.domain.mcp.service import McpService
from app.domain.user import User
from app.services.mcp import mcp_session_context

router = APIRouter(tags=["mcps"])


class McpCheckResponse(BaseModel):
    """Response from MCP check/probe."""

    status: str  # "ok" | "error"
    tool_count: int


@router.get("/mcps", response_model=list[McpResponse])
async def list_mcps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List current user's MCPs."""
    service = McpService(db)
    return service.list(current_user.id)


@router.get("/mcps/{mcp_id}", response_model=McpResponse)
async def get_mcp(
    mcp_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get one MCP by id."""
    service = McpService(db)
    mcp = service.get(mcp_id, current_user.id)
    if mcp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")
    return mcp


@router.post("/mcps", response_model=McpResponse, status_code=status.HTTP_201_CREATED)
async def create_mcp(
    body: McpCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new MCP config."""
    try:
        service = McpService(db)
        return service.create(current_user.id, body.name, body.config)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.put("/mcps/{mcp_id}", response_model=McpResponse)
async def update_mcp(
    mcp_id: UUID,
    body: McpUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update MCP name and/or config."""
    try:
        service = McpService(db)
        mcp = service.update(
            mcp_id,
            current_user.id,
            name=body.name,
            config=body.config,
        )
        if mcp is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")
        return mcp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/mcps/{mcp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp(
    mcp_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an MCP config."""
    service = McpService(db)
    if not service.delete(mcp_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")


@router.post("/mcps/{mcp_id}/check", response_model=McpCheckResponse)
async def check_mcp(
    mcp_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Connect to MCP, list tools, update cached status and tool count, return result."""
    service = McpService(db)
    mcp = service.get(mcp_id, current_user.id)
    if mcp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")
    try:
        async with mcp_session_context(mcp.config) as session:
            list_result = await session.list_tools()
            tool_count = len(list_result.tools)
        service.update_status(mcp_id, current_user.id, "ok", tool_count)
        return McpCheckResponse(status="ok", tool_count=tool_count)
    except Exception:
        service.update_status(mcp_id, current_user.id, "error", None)
        return McpCheckResponse(status="error", tool_count=0)
