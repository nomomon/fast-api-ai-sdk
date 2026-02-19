"""Skill repository for data access.

Default skills: folder-based layout skills/<skill-name>/SKILL.md (read-only).
User skills: UserSkillRepository backed by DB.
"""

import re
from pathlib import Path
from uuid import UUID

import frontmatter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.skill.models import UserSkill


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

    def list_by_user(self, user_id: UUID) -> list[UserSkill]:
        """Return all user skills for the user, ordered by name."""
        return (
            self.db.query(UserSkill)
            .filter(UserSkill.user_id == user_id)
            .order_by(UserSkill.name)
            .all()
        )

    def get_by_id(self, skill_id: UUID, user_id: UUID) -> UserSkill | None:
        """Return a user skill by id if it belongs to the user."""
        return (
            self.db.query(UserSkill)
            .filter(UserSkill.id == skill_id, UserSkill.user_id == user_id)
            .first()
        )

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

    def create(self, user_id: UUID, name: str, description: str, content: str) -> UserSkill | None:
        """Create a new user skill. Returns None if name invalid or already exists."""
        if not _validate_skill_name(name):
            return None
        existing = (
            self.db.query(UserSkill)
            .filter(UserSkill.user_id == user_id, UserSkill.name == name)
            .first()
        )
        if existing is not None:
            return None
        try:
            row = UserSkill(
                user_id=user_id,
                name=name,
                description=description or "",
                content=content or "",
            )
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
            return row
        except IntegrityError:
            self.db.rollback()
            return None
        except Exception:
            self.db.rollback()
            return None

    def create_or_update(
        self, user_id: UUID, name: str, description: str, content: str
    ) -> UserSkill | None:
        """Create or update a user skill by (user_id, name). Returns None if name invalid."""
        if not _validate_skill_name(name):
            return None
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
            self.db.refresh(row)
            return row
        except IntegrityError:
            self.db.rollback()
            return None
        except Exception:
            self.db.rollback()
            return None

    def update(
        self,
        skill_id: UUID,
        user_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        content: str | None = None,
    ) -> UserSkill | None:
        """Update a user skill by id. Returns None if not found or name invalid."""
        row = self.get_by_id(skill_id, user_id)
        if row is None:
            return None
        if name is not None:
            if not _validate_skill_name(name):
                return None
            row.name = name
        if description is not None:
            row.description = description
        if content is not None:
            row.content = content
        try:
            self.db.commit()
            self.db.refresh(row)
            return row
        except IntegrityError:
            self.db.rollback()
            return None
        except Exception:
            self.db.rollback()
            return None

    def delete(self, skill_id: UUID, user_id: UUID) -> bool:
        """Delete a user skill by id. Returns True if deleted."""
        row = self.get_by_id(skill_id, user_id)
        if row is None:
            return False
        try:
            self.db.delete(row)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
