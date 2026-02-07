"""Update or create a user skill via SkillService (DB only)."""

from app.core.request_context import get_current_db, get_current_user_id
from app.domain.skill.service import SkillService


def update_skill(skill_name: str, description: str, body: str) -> bool:
    """Create or update the current user's skill in the database.

    Does not write to files. User-created skills are stored per user in the
    database. Skill name must match Agent Skills spec: lowercase letters,
    numbers, hyphens; 1-64 chars; no leading or trailing hyphen.

    Args:
        skill_name: Name of the skill (must be valid per spec).
        description: Description (what the skill does, when to use it).
        body: Markdown body (instructions and content).

    Returns:
        True if the skill was created or updated successfully, False if
        name is invalid, write failed, or no authenticated user context.
    """
    db = get_current_db()
    user_id = get_current_user_id()
    if user_id is None:
        return False
    service = SkillService(db=db)
    return service.update_skill(skill_name, description, body, user_id=user_id)
