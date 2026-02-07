"""Load a skill by name via SkillService (default MD + user DB)."""

from app.core.request_context import get_current_db, get_current_user_id
from app.domain.skill.service import SkillService


def load_skill(skill_name: str) -> str | None:
    """Get a skill by name.

    Resolves user skill from the database first (if authenticated), then
    default skill from skills/<skill_name>/SKILL.md. Skill name must match
    the directory name or user skill name (Agent Skills spec).

    Args:
        skill_name: Name of the skill to load (matches folder name or user skill).

    Returns:
        Skill content (body) as a string, or None if not found.
    """
    db = get_current_db()
    user_id = get_current_user_id()
    service = SkillService(db=db)
    return service.get_content_by_name(skill_name, user_id=user_id)
