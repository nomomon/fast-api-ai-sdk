"""Load a skill by name via SkillService (skills/<name>/SKILL.md)."""

from app.domain.skill.service import SkillService


def load_skill(skill_name: str) -> str | None:
    """Get a skill by name.

    Loads the skill body from skills/<skill_name>/SKILL.md via SkillService.
    Skill name must match the directory name (Agent Skills spec).

    Args:
        skill_name: Name of the skill to load (matches folder name).

    Returns:
        Skill content (SKILL.md body) as a string, or None if not found.
    """
    return SkillService().get_content_by_name(skill_name)
