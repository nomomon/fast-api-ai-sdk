"""Skill service for business logic."""

from uuid import UUID
from xml.sax.saxutils import escape

from sqlalchemy.orm import Session

from app.domain.skill.repository import SkillRepository, UserSkillRepository
from app.domain.skill.schemas import Skill, SkillListResponse, SkillMetadata


class SkillService:
    """Service for skill business logic.

    Default skills are read from files (skills/<name>/SKILL.md).
    User skills are stored in the database. When db is provided and user_id
    is set, listing and loading merge both (user skill shadows default by name).
    """

    def __init__(self, db: Session | None = None):
        """Initialize service with repositories.

        Args:
            db: Optional database session for user-skill operations.
        """
        self._default_repo = SkillRepository()
        self._user_repo = UserSkillRepository(db) if db else None

    def get_metadata_list(self, user_id: UUID | None = None) -> list[SkillMetadata]:
        """Return list of skill metadata (default + user). User skills shadow defaults by name."""
        by_name: dict[str, dict] = {}
        for d in self._default_repo.get_all_metadata():
            by_name[d["name"]] = d
        if user_id and self._user_repo:
            for d in self._user_repo.get_all_metadata(user_id):
                by_name[d["name"]] = d
        return [SkillMetadata(**v) for v in by_name.values()]

    def get_available_skills_xml(self, user_id: UUID | None = None) -> str:
        """Return available_skills XML for system prompt (default + user skills)."""
        skills = self._metadata_list_for_xml(user_id)
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

    def _metadata_list_for_xml(self, user_id: UUID | None = None) -> list[dict]:
        """Merge default + user metadata; user shadows default by name."""
        by_name: dict[str, dict] = {}
        for d in self._default_repo.get_all_metadata():
            by_name[d["name"]] = d
        if user_id and self._user_repo:
            for d in self._user_repo.get_all_metadata(user_id):
                by_name[d["name"]] = d
        return list(by_name.values())

    def get_all(self, user_id: UUID | None = None) -> SkillListResponse:
        """Get all skills (default + user; user shadows by name)."""
        by_name: dict[str, dict] = {}
        for d in self._default_repo.get_all():
            by_name[d["name"]] = d
        if user_id and self._user_repo:
            for d in self._user_repo.get_all_metadata(user_id):
                name = d["name"]
                content = self._user_repo.get_content_by_name(user_id, name)
                by_name[name] = {
                    "name": name,
                    "description": d["description"],
                    "content": content,
                    "path": None,
                }
        skills = [Skill(**v) for v in by_name.values()]
        return SkillListResponse(skills=skills)

    def get_content_by_name(self, name: str, user_id: UUID | None = None) -> str | None:
        """Get skill body by name. If user_id set, user skill first then default."""
        if user_id and self._user_repo:
            content = self._user_repo.get_content_by_name(user_id, name)
            if content is not None:
                return content
        return self._default_repo.get_content_by_name(name)

    def update_skill(
        self,
        skill_name: str,
        description: str,
        body: str,
        user_id: UUID | None = None,
    ) -> bool:
        """Create or update a user skill in the database only.

        Does not write to files. If user_id is None or no db, returns False.
        """
        if user_id is None or self._user_repo is None:
            return False
        return self._user_repo.create_or_update(user_id, skill_name, description or "", body or "")

    def get_user_skills(self, user_id: UUID) -> list[dict]:
        """Return list of skill dicts for the user (dashboard API)."""
        if self._user_repo is None:
            return []
        return self._user_repo.get_all_for_user(user_id)

    def get_user_skill_by_id(self, user_id: UUID, skill_id: UUID) -> dict | None:
        """Return one skill by id if it belongs to the user, else None."""
        if self._user_repo is None:
            return None
        return self._user_repo.get_by_id(user_id, skill_id)

    def update_user_skill_by_id(
        self,
        user_id: UUID,
        skill_id: UUID,
        *,
        description: str | None = None,
        content: str | None = None,
    ) -> bool:
        """Update description and/or content by id. Returns True if updated."""
        if self._user_repo is None:
            return False
        return self._user_repo.update_by_id(
            user_id, skill_id, description=description, content=content
        )

    def delete_user_skill_by_id(self, user_id: UUID, skill_id: UUID) -> bool:
        """Delete user skill by id. Returns True if deleted."""
        if self._user_repo is None:
            return False
        return self._user_repo.delete_by_id(user_id, skill_id)
