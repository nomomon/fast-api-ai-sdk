"""Skill repository for data access.

Loads skills from folder-based layout: skills/<skill-name>/SKILL.md
with YAML frontmatter (name, description) and Markdown body.
"""

from pathlib import Path

import frontmatter


class SkillRepository:
    """Repository for skill data access operations.

    Discovers skills as subdirs of ``skills/`` that contain SKILL.md.
    """

    SKILLS_DIR = Path(__file__).resolve().parent / "skills"

    def _skill_paths(self) -> list[Path]:
        """Paths to SKILL.md files (one per skill directory)."""
        if not self.SKILLS_DIR.is_dir():
            return []
        return sorted(self.SKILLS_DIR.glob("*/SKILL.md"))

    def get_all_metadata(self) -> list[dict]:
        """Load metadata (name, description, path) from frontmatter only.

        Skips skills where frontmatter name does not match directory name.
        """
        result: list[dict] = []
        for path in self._skill_paths():
            try:
                post = frontmatter.load(path)
                meta = post.metadata
                dir_name = path.parent.name
                name = meta.get("name")
                if name is None or name != dir_name:
                    continue
                description = meta.get("description") or ""
                result.append(
                    {
                        "name": name,
                        "description": description,
                        "path": str(path.resolve()),
                    }
                )
            except Exception:
                continue
        return result

    def get_all(self) -> list[dict]:
        """Get all skills (metadata + content)."""
        result: list[dict] = []
        for path in self._skill_paths():
            try:
                post = frontmatter.load(path)
                meta = post.metadata
                dir_name = path.parent.name
                name = meta.get("name")
                if name is None or name != dir_name:
                    continue
                description = meta.get("description") or ""
                content = (post.content or "").strip()
                result.append(
                    {
                        "name": name,
                        "description": description,
                        "path": str(path.resolve()),
                        "content": content or None,
                    }
                )
            except Exception:
                continue
        return result

    def get_by_name(self, name: str) -> dict | None:
        """Get skill by name (directory name)."""
        for skill in self.get_all():
            if skill["name"] == name:
                return skill
        return None

    def get_content_by_name(self, name: str) -> str | None:
        """Load full SKILL.md for the given name and return body only."""
        skill_file = self.SKILLS_DIR / name / "SKILL.md"
        if not skill_file.is_file():
            return None
        try:
            post = frontmatter.load(skill_file)
            return (post.content or "").strip() or None
        except Exception:
            return None
