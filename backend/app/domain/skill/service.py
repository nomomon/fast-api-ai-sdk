"""Skill service for business logic."""

from xml.sax.saxutils import escape

from app.domain.skill.repository import SkillRepository
from app.domain.skill.schemas import Skill, SkillListResponse, SkillMetadata


class SkillService:
    """Service for skill business logic."""

    def __init__(self):
        """Initialize service with repository."""
        self.repository = SkillRepository()

    def get_metadata_list(self) -> list[SkillMetadata]:
        """Return list of skill metadata (name, description, path)."""
        data = self.repository.get_all_metadata()
        return [SkillMetadata(**d) for d in data]

    def get_available_skills_xml(self) -> str:
        """Return available_skills XML for system prompt."""
        skills = self.repository.get_all_metadata()
        parts: list[str] = []
        for s in skills:
            name_esc = escape(s["name"])
            desc_esc = escape(s["description"])
            buf = (
                "\t<skill>\n"
                f"\t\t<name>{name_esc}</name>\n"
                f"\t\t<description>{desc_esc}</description>"
                "\t\n</skill>"
            )
            parts.append(buf)
        return "<available_skills>\n" + "\n".join(parts) + "\n</available_skills>"

    def get_all(self) -> SkillListResponse:
        """Get all skills (metadata + content)."""
        skills_data = self.repository.get_all()
        skills = [Skill(**s) for s in skills_data]
        return SkillListResponse(skills=skills)

    def get_content_by_name(self, name: str) -> str | None:
        """Get skill body content by name (used by load_skill tool)."""
        return self.repository.get_content_by_name(name)
