"""Core abstractions for the skills system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Skill:
    """A skill with its metadata and optional body content.

    `content` is None when only metadata has been loaded (lazy).
    `metadata` holds any extra frontmatter keys beyond name and description.
    """

    name: str
    description: str
    content: str | None = None
    metadata: dict = field(default_factory=dict)


class SkillSource(ABC):
    """Abstract source of skills.

    Implement this to plug in any backend (filesystem, database, API, etc.).

    Example::

        class DBSkillSource(SkillSource):
            def __init__(self, repo: UserSkillRepository, user_id: UUID): ...

            def list_metadata(self) -> list[Skill]:
                return [Skill(name=r.name, description=r.description) for r in ...]

            def load_content(self, name: str) -> str | None:
                return repo.get_content_by_name(user_id, name)
    """

    @abstractmethod
    def list_metadata(self) -> list[Skill]:
        """Return all skills with name and description populated. content may be None."""

    @abstractmethod
    def load_content(self, name: str) -> str | None:
        """Return body content for the named skill, or None if not found."""
