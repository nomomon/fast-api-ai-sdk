from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint - placeholder for now.
    Will be implemented later with AI service integration.
    """
    # TODO: Implement chat logic with AI service
    return ChatResponse(
        message="Chat endpoint - to be implemented",
        role="assistant"
    )

