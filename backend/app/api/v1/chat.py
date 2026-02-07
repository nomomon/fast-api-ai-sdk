"""Chat API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.domain.model.service import ModelService
from app.domain.prompt.service import PromptService
from app.domain.skill.service import SkillService
from app.domain.user import User
from app.services.ai.adapters.messages import ClientMessage
from app.services.ai.adapters.streaming import SSEFormatter, patch_response_with_headers
from app.services.ai.agents.chat_agent import ChatAgent
from app.services.ai.agents.research_agent import ResearchAgent

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request schema."""

    messages: list[ClientMessage]
    modelId: str | None = None
    promptId: str | None = None
    agentId: str = "chat"


@router.post("/chat")
async def handle_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Chat endpoint compatible with Vercel AI SDK.
    Dispatches to ChatAgent or ResearchAgent based on agentId.
    """
    messages = request.messages
    model_id = request.modelId
    prompt_id = request.promptId
    agent_id = request.agentId

    model_service = ModelService()
    if model_id is None:
        model_id = model_service.get_default_model_id()
    elif not model_service.is_valid_model_id(model_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid modelId: {model_id}. Use GET /api/v1/models for allowed models.",
        )

    skills_xml = SkillService().get_available_skills_xml(include_location=False)
    if prompt_id:
        prompt_service = PromptService()
        prompt_content = prompt_service.get_by_id(prompt_id)
        if prompt_content:
            system_content = prompt_content + "\n\n" + skills_xml
        else:
            system_content = skills_xml
    else:
        system_content = skills_xml
    system_message = ClientMessage(role="system", content=system_content)
    messages = [system_message] + messages

    if agent_id == "chat":
        agent = ChatAgent(model_id)
        provider_stream = agent.stream_chat(messages)
    elif agent_id == "research":
        agent = ResearchAgent(model_id)
        provider_stream = agent.execute(messages)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown agentId: {agent_id}. Supported: chat, research",
        )

    formatted_stream = SSEFormatter.format_stream(provider_stream)

    response = StreamingResponse(
        formatted_stream,
        media_type="text/event-stream",
    )
    return patch_response_with_headers(response)
