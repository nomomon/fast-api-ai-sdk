"""AI chat endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.ai.adapters.messages import ClientMessage, convert_to_openai_messages
from src.ai.formatter import format_events, patch_response_with_headers
from src.ai.handler import run_agent
from src.ai.models.repository import ModelRepository
from src.auth.dependencies import get_current_user
from src.database import get_db
from src.user.models import User

from .mcp import router as mcp_router
from .models import router as models_router
from .prompts import router as prompts_router
from .skills import router as skills_router

router = APIRouter(prefix="/ai", tags=["ai"])

router.include_router(models_router)
router.include_router(mcp_router)
router.include_router(prompts_router)
router.include_router(skills_router)

_model_repo = ModelRepository()


class ChatRequest(BaseModel):
    messages: list[ClientMessage]
    modelId: str | None = None


@router.post("")
async def handle_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model_id = request.modelId or _model_repo.get_default_id()
    if request.modelId and not _model_repo.exists(request.modelId):
        raise HTTPException(status_code=400, detail=f"Invalid modelId: {request.modelId}")
    messages = convert_to_openai_messages(request.messages)
    response = StreamingResponse(
        format_events(run_agent(messages, model_id, user_id=current_user.id, db=db)),
        media_type="text/event-stream",
    )
    return patch_response_with_headers(response)
