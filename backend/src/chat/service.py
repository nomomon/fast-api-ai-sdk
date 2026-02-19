"""Chat service for chat orchestration logic."""

from collections.abc import AsyncGenerator
from uuid import UUID

from sqlalchemy.orm import Session

from src.ai.adapters.messages import ClientMessage
from src.ai.adapters.streaming import SSEFormatter
from src.ai.agents.registry import get_agent
from src.ai.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS
from src.chat.protocols import McpConfigProvider
from src.mcp.client import get_user_mcp_tools_context
from src.mcp.repository import UserMcpRepository
from src.model.repository import ModelRepository
from src.prompt.repository import PromptRepository
from src.request_context import set_current_db, set_current_user_id
from src.skill import service as skill_service


class ChatService:
    """Service for chat orchestration: validation, message preparation, agent dispatch."""

    def __init__(
        self,
        db: Session,
        mcp_config_provider: McpConfigProvider | None = None,
    ):
        """Initialize service with database session and optional MCP config provider.

        When mcp_config_provider is None, uses UserMcpRepository(db) as default.
        Inject a custom provider for testing (e.g. fake returning fixed configs).
        """
        self._db = db
        self._model_repo = ModelRepository()
        self._prompt_repo = PromptRepository()
        self._skill_svc = skill_service.SkillService(db=db)
        self._mcp_provider: McpConfigProvider = mcp_config_provider or UserMcpRepository(db)

    def prepare_messages(
        self,
        model_id: str | None,
        prompt_id: str | None,
        agent_id: str,
        user_id: UUID | None,
        messages: list[ClientMessage],
    ) -> tuple[str, list[ClientMessage]]:
        """Validate inputs and prepare messages with prompt/skills. Returns (model_id, messages).

        Raises:
            ValueError: On validation failure (invalid model, prompt, or agent)
        """
        if model_id is None:
            model_id = self._model_repo.get_default_id()
        elif not self._model_repo.exists(model_id):
            raise ValueError(
                f"Invalid modelId: {model_id}. Use GET /api/models for allowed models."
            )

        if prompt_id:
            system_content = self._prompt_repo.get_content_by_id(prompt_id)
            if system_content is None:
                raise ValueError(
                    f"Invalid promptId: {prompt_id}. Use GET /api/prompts for allowed prompts."
                )
            system_prompt = ClientMessage(role="system", content=system_content)
            messages = [system_prompt] + messages

        if user_id is not None:
            skills_content = self._skill_svc.get_available_skills_xml(user_id=user_id)
            skills_prompt = ClientMessage(role="system", content=skills_content)
            messages = [skills_prompt] + messages

        return model_id, messages

    async def stream_chat_events(
        self,
        model_id: str,
        agent_id: str,
        messages: list[ClientMessage],
        user_id: UUID | None,
    ) -> AsyncGenerator[str, None]:
        """Stream chat events as SSE-formatted strings. Handles MCP, agent dispatch, context."""
        agent = get_agent(agent_id, model_id)

        if agent_id == "chat":
            mcp_configs: list[tuple[str, dict]] = []
            if user_id is not None:
                mcp_configs = self._mcp_provider.list_configs(user_id)

            async def _stream_with_context():
                set_current_user_id(user_id)
                set_current_db(self._db)
                try:
                    async with get_user_mcp_tools_context(
                        mcp_configs, TOOL_DEFINITIONS, AVAILABLE_TOOLS
                    ) as (tool_definitions, available_tools):
                        provider_stream = agent.stream_chat(
                            messages,
                            tool_definitions=tool_definitions,
                            available_tools=available_tools,
                        )
                        formatted = SSEFormatter.format_stream(provider_stream)
                        async for event in formatted:
                            yield event
                finally:
                    set_current_user_id(None)
                    set_current_db(None)

            async for event in _stream_with_context():
                yield event
        else:
            provider_stream = agent.execute(messages)
            formatted = SSEFormatter.format_stream(provider_stream)

            async def _stream_with_context():
                set_current_user_id(user_id)
                set_current_db(self._db)
                try:
                    async for event in formatted:
                        yield event
                finally:
                    set_current_user_id(None)
                    set_current_db(None)

            async for event in _stream_with_context():
                yield event
