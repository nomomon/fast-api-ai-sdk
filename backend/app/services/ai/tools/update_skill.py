"""Update or create a skill (SKILL.md) via SkillService."""

from app.domain.skill.service import SkillService


def update_skill(skill_name: str, description: str, body: str) -> bool:
    """Update or create a skill file.

    Writes skills/<skill_name>/SKILL.md with the given frontmatter (name,
    description) and body. If the file exists, it is overwritten. If the
    directory does not exist, it is created (creating new skills is
    supported but discouraged). Skill name must match Agent Skills spec:
    lowercase letters, numbers, hyphens; 1-64 chars; no leading or
    trailing hyphen.

    Args:
        skill_name: Name of the skill (matches folder name; must be valid).
        description: Frontmatter description (what the skill does, when to use it).
        body: Markdown body (instructions and content after the frontmatter).

    Returns:
        True if the skill was written successfully, False if name is invalid
        or write failed.
    """
    return SkillService().update_skill(skill_name, description, body)
