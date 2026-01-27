from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.models.user import User
from app.providers import ProviderFactory
from app.utils.auth import get_current_user
from app.utils.prompt import ClientMessage
from app.utils.stream import SSEFormatter, patch_response_with_headers

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    messages: list[ClientMessage]
    modelId: str | None = None


@router.post("/chat")
async def handle_chat_data(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Chat endpoint compatible with Vercel AI SDK.
    Handles streaming chat completions with tool support through provider abstraction.
    """
    messages = request.messages
    model = request.modelId

    provider_name, model_id = model.split("/", 1)

    provider = ProviderFactory.get_provider(provider_name)

    # Get provider stream and format it as SSE
    provider_stream = provider.stream_chat(messages, model_id)
    formatted_stream = SSEFormatter.format_stream(provider_stream)

    # Create streaming response
    response = StreamingResponse(
        formatted_stream,
        media_type="text/event-stream",
    )
    return patch_response_with_headers(response)
