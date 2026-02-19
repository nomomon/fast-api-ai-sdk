"""Chat API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.ai.adapters.streaming import patch_response_with_headers
from src.auth.dependencies import get_current_user
from src.chat.schemas import ChatRequest
from src.chat.service import ChatService
from src.database import get_db
from src.request_context import set_current_db, set_current_user_id
from src.user.models import User

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def handle_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Chat endpoint compatible with Vercel AI SDK.
    Dispatches to ChatAgent or ResearchAgent based on agentId.
    """
    set_current_user_id(current_user.id)
    set_current_db(db)
    try:
        service = ChatService(db)
        model_id, messages = service.prepare_messages(
            model_id=request.modelId,
            prompt_id=request.promptId,
            agent_id=request.agentId,
            user_id=current_user.id,
            messages=request.messages,
        )
        response = StreamingResponse(
            service.stream_chat_events(
                model_id=model_id,
                agent_id=request.agentId,
                messages=messages,
                user_id=current_user.id,
            ),
            media_type="text/event-stream",
        )
        return patch_response_with_headers(response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    finally:
        set_current_user_id(None)
        set_current_db(None)
