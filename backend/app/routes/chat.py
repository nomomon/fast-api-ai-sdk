from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.providers import ProviderFactory
from app.utils.prompt import ClientMessage
from app.utils.stream import patch_response_with_headers

router = APIRouter()


class ChatRequest(BaseModel):
    messages: list[ClientMessage]
    model: str | None = None
    modelId: str | None = None


@router.post("/chat")
async def handle_chat_data(request: ChatRequest):
    """
    Chat endpoint compatible with Vercel AI SDK.
    Handles streaming chat completions with tool support through provider abstraction.
    """
    messages = request.messages
    model = request.modelId

    provider_name, model_id = model.split("/", 1)

    provider = ProviderFactory.get_provider(provider_name)

    # Create streaming response
    response = StreamingResponse(
        provider.stream_chat(messages, model_id),
        media_type="text/event-stream",
    )
    return patch_response_with_headers(response)
