from typing import List

from fastapi import APIRouter, Query, Request as FastAPIRequest
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel

from app.config import settings
from app.utils.prompt import ClientMessage, convert_to_openai_messages
from app.utils.stream import patch_response_with_headers, stream_text
from app.utils.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS

router = APIRouter()


class ChatRequest(BaseModel):
    messages: List[ClientMessage]


@router.post("/chat")
async def handle_chat_data(request: ChatRequest, protocol: str = Query('data')):
    """
    Chat endpoint compatible with Vercel AI SDK.
    Handles streaming chat completions with tool support.
    """
    messages = request.messages
    
    # Convert to OpenAI format
    openai_messages = convert_to_openai_messages(messages)

    # Initialize OpenAI client
    client = OpenAI(api_key=settings.openai_api_key)
    
    # Create streaming response
    response = StreamingResponse(
        stream_text(client, openai_messages, TOOL_DEFINITIONS, AVAILABLE_TOOLS, protocol, settings.openai_model),
        media_type="text/event-stream",
    )
    return patch_response_with_headers(response, protocol)
