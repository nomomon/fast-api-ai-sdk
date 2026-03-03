"""FileSkillSource: loads skills from a directory of SKILL.md files."""

from __future__ import annotations

import re
from pathlib import Path

from ai.agent.skills.base import Skill, SkillSource

# Default built-in skills directory: ai/ai/skills/
_DEFAULT_SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / "skills"


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse YAML frontmatter from markdown text using stdlib only.

    Handles flat ``key: value`` pairs (the SKILL.md format).
    Returns ``(metadata_dict, body_string)``.
    """
    m = re.match(r"^---\n(.*?)\n---\n?(.*)", text, re.DOTALL)
    if not m:
        return {}, text.strip()

    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()

    return meta, m.group(2).strip()


class FileSkillSource(SkillSource):
    """Loads skills from a directory of ``<skill-name>/SKILL.md`` files.

    Each skill lives in its own subdirectory and contains a SKILL.md with
    YAML frontmatter (``name``, ``description``) followed by the skill body.
    The frontmatter ``name`` must match the directory name.

    Args:
        skills_dir: Directory containing skill subdirectories.
                    Defaults to ``ai/ai/skills/`` (the built-in skills).

    Example::

        source = FileSkillSource()                          # built-ins
        source = FileSkillSource(Path("/my/custom/skills")) # custom dir
    """

    def __init__(self, skills_dir: Path | None = None) -> None:
        self._dir = skills_dir or _DEFAULT_SKILLS_DIR

    def list_metadata(self) -> list[Skill]:
        """Return metadata for all valid skills in the directory."""
        if not self._dir.is_dir():
            return []

        skills: list[Skill] = []
        for skill_file in sorted(self._dir.glob("*/SKILL.md")):
            try:
                text = skill_file.read_text(encoding="utf-8")
                meta, _ = _parse_frontmatter(text)
                name = meta.get("name", "")
                if not name or name != skill_file.parent.name:
                    continue
                description = meta.get("description", "")
                extra = {
                    k: v for k, v in meta.items() if k not in ("name", "description")
                }
                skills.append(Skill(name=name, description=description, metadata=extra))
            except Exception:
                continue

        return skills

    def load_content(self, name: str) -> str | None:
        """Return body content for the named skill, or None if not found."""
        skill_file = self._dir / name / "SKILL.md"
        if not skill_file.is_file():
            return None
        try:
            text = skill_file.read_text(encoding="utf-8")
            _, body = _parse_frontmatter(text)
            return body or None
        except Exception:
            return None
