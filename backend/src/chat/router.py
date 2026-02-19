"""Chat API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.ai.adapters.messages import ClientMessage
from src.ai.adapters.streaming import SSEFormatter, patch_response_with_headers
from src.ai.agents.chat_agent import ChatAgent
from src.ai.agents.research_agent import ResearchAgent
from src.ai.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS
from src.auth.dependencies import get_current_user
from src.chat.schemas import ChatRequest
from src.database import get_db
from src.mcp.client import get_user_mcp_tools_context
from src.mcp.service import McpService
from src.model.repository import ModelRepository
from src.prompt.repository import PromptRepository
from src.request_context import set_current_db, set_current_user_id
from src.skill import service as skill_service
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
        messages = request.messages
        model_id = request.modelId
        prompt_id = request.promptId
        agent_id = request.agentId

        model_repo = ModelRepository()
        if model_id is None:
            model_id = model_repo.get_default_id()
        elif not model_repo.exists(model_id):
            raise HTTPException(
                status_code=400,
                detail=(f"Invalid modelId: {model_id}. Use GET /api/models for allowed models."),
            )

        if prompt_id:
            prompt_repo = PromptRepository()
            system_content = prompt_repo.get_content_by_id(prompt_id)
            if system_content is None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Invalid promptId: {prompt_id}. Use GET /api/prompts for allowed prompts."
                    ),
                )
            system_prompt = ClientMessage(role="system", content=system_content)
            messages = [system_prompt] + messages

        if current_user.id is not None:
            skill_svc = skill_service.SkillService(db=db)
            skills_content = skill_svc.get_available_skills_xml(user_id=current_user.id)
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
