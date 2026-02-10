"""Chat API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.request_context import set_current_db, set_current_user_id
from app.domain.mcp.service import McpService
from app.domain.model.service import ModelService
from app.domain.prompt.service import PromptService
from app.domain.skill.service import SkillService
from app.domain.user import User
from app.services.ai.adapters.messages import ClientMessage
from app.services.ai.adapters.streaming import SSEFormatter, patch_response_with_headers
from app.services.ai.agents.chat_agent import ChatAgent
from app.services.ai.agents.research_agent import ResearchAgent
from app.services.ai.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS
from app.services.mcp import get_user_mcp_tools_context

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

        if prompt_id:
            prompt_service = PromptService()
            system_content = prompt_service.get_by_id(prompt_id)
            system_prompt = ClientMessage(role="system", content=system_content)
            messages = [system_prompt] + messages

        if current_user.id is not None:
            skills_content = SkillService(db=db).get_available_skills_xml(user_id=current_user.id)
            skills_prompt = ClientMessage(role="system", content=skills_content)
            messages = [skills_prompt] + messages

        _user_id = current_user.id
        _db = db

        if agent_id == "chat":
            mcp_service = McpService(db)
            mcp_list = mcp_service.list(current_user.id) if current_user.id else []
            mcp_configs = [(m.name, m.config) for m in mcp_list]

            async def stream_with_context_cleanup():
                set_current_user_id(_user_id)
                set_current_db(_db)
                try:
                    async with get_user_mcp_tools_context(
                        mcp_configs, TOOL_DEFINITIONS, AVAILABLE_TOOLS
                    ) as (tool_definitions, available_tools):
                        agent = ChatAgent(model_id)
                        provider_stream = agent.stream_chat(
                            messages,
                            tool_definitions=tool_definitions,
                            available_tools=available_tools,
                        )
                        formatted_stream = SSEFormatter.format_stream(provider_stream)
                        async for event in formatted_stream:
                            yield event
                finally:
                    set_current_user_id(None)
                    set_current_db(None)
        elif agent_id == "research":
            agent = ResearchAgent(model_id)
            provider_stream = agent.execute(messages)
            formatted_stream = SSEFormatter.format_stream(provider_stream)

            async def stream_with_context_cleanup():
                set_current_user_id(_user_id)
                set_current_db(_db)
                try:
                    async for event in formatted_stream:
                        yield event
                finally:
                    set_current_user_id(None)
                    set_current_db(None)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown agentId: {agent_id}. Supported: chat, research",
            )

        response = StreamingResponse(
            stream_with_context_cleanup(),
            media_type="text/event-stream",
        )
        return patch_response_with_headers(response)
    finally:
        set_current_user_id(None)
        set_current_db(None)
