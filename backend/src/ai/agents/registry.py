"""Agent registry: map agent_id to factory for Open/Closed extension."""

from collections.abc import Callable

from src.ai.agents.base import BaseAgent
from src.ai.agents.chat_agent import ChatAgent
from src.ai.agents.research_agent import ResearchAgent

# (model_id: str) -> BaseAgent
AGENT_REGISTRY: dict[str, Callable[[str], BaseAgent]] = {
    "chat": lambda model_id: ChatAgent(model_id),
    "research": lambda model_id: ResearchAgent(model_id),
}


def get_agent(agent_id: str, model_id: str) -> BaseAgent:
    """Return agent for agent_id and model_id. Raises ValueError if agent_id unknown."""
    factory = AGENT_REGISTRY.get(agent_id)
    if factory is None:
        supported = ", ".join(sorted(AGENT_REGISTRY))
        raise ValueError(f"Unknown agentId: {agent_id}. Supported: {supported}")
    return factory(model_id)
