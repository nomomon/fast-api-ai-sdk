"""Skill repository for data access.

Default skills: folder-based layout skills/<skill-name>/SKILL.md (read-only).
User skills: UserSkillRepository backed by DB.
"""

import re
from pathlib import Path
from uuid import UUID

import frontmatter
from sqlalchemy.orm import Session

from app.domain.skill.models import UserSkill


def _validate_skill_name(name: str) -> bool:
    """Validate skill name per Agent Skills spec: 1-64 chars, lowercase, hyphens."""
    if not (1 <= len(name) <= 64):
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", name))


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


class UserSkillRepository:
    """Repository for user-owned skills stored in the database."""

    def __init__(self, db: Session):
        self.db = db

    def get_all_metadata(self, user_id: UUID) -> list[dict]:
        """Return metadata (name, description) for all skills owned by the user."""
        rows = (
            self.db.query(UserSkill)
            .filter(UserSkill.user_id == user_id)
            .order_by(UserSkill.name)
            .all()
        )
        return [{"name": r.name, "description": r.description or "", "path": None} for r in rows]

    def get_content_by_name(self, user_id: UUID, name: str) -> str | None:
        """Return skill body content for the user's skill by name, or None."""
        row = (
            self.db.query(UserSkill)
            .filter(UserSkill.user_id == user_id, UserSkill.name == name)
            .first()
        )
        if row is None:
            return None
        return (row.content or "").strip() or None

    def get_all_for_user(self, user_id: UUID) -> list[dict]:
        """Return full rows (id, name, description, content, created_at, updated_at) for user."""
        rows = (
            self.db.query(UserSkill)
            .filter(UserSkill.user_id == user_id)
            .order_by(UserSkill.name)
            .all()
        )
        return [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description or "",
                "content": r.content or "",
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            for r in rows
        ]

    def get_by_id(self, user_id: UUID, skill_id: UUID) -> dict | None:
        """Return one skill row as dict if it belongs to the user, else None."""
        row = (
            self.db.query(UserSkill)
            .filter(UserSkill.id == skill_id, UserSkill.user_id == user_id)
            .first()
        )
        if row is None:
            return None
        return {
            "id": row.id,
            "name": row.name,
            "description": row.description or "",
            "content": row.content or "",
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    def update_by_id(
        self,
        user_id: UUID,
        skill_id: UUID,
        *,
        description: str | None = None,
        content: str | None = None,
    ) -> bool:
        """Update description and/or content by id. Row must belong to user_id.

        Returns True if updated.
        """
        row = (
            self.db.query(UserSkill)
            .filter(UserSkill.id == skill_id, UserSkill.user_id == user_id)
            .first()
        )
        if row is None:
            return False
        try:
            if description is not None:
                row.description = description
            if content is not None:
                row.content = content
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def delete_by_id(self, user_id: UUID, skill_id: UUID) -> bool:
        """Delete skill by id if it belongs to user_id. Returns True if deleted."""
        row = (
            self.db.query(UserSkill)
            .filter(UserSkill.id == skill_id, UserSkill.user_id == user_id)
            .first()
        )
        if row is None:
            return False
        try:
            self.db.delete(row)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def create_or_update(self, user_id: UUID, name: str, description: str, content: str) -> bool:
        """Create or update a user skill by (user_id, name). Returns False if name invalid."""
        if not _validate_skill_name(name):
            return False
        try:
            row = (
                self.db.query(UserSkill)
                .filter(UserSkill.user_id == user_id, UserSkill.name == name)
                .first()
            )
            if row is None:
                row = UserSkill(
                    user_id=user_id,
                    name=name,
                    description=description or "",
                    content=content or "",
                )
                self.db.add(row)
            else:
                row.description = description or ""
                row.content = content or ""
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
