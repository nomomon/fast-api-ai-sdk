"""Skill repository for data access.

User skills: UserSkillRepository backed by DB.
Default skills: use FileSkillSource from the ai package.
"""

import re
from uuid import UUID

from ai.agent.skills import Skill as AiSkill
from ai.agent.skills import SkillSource
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.skills.models import UserSkill


def _validate_skill_name(name: str) -> bool:
    """Validate skill name per Agent Skills spec: 1-64 chars, lowercase, hyphens."""
    if not (1 <= len(name) <= 64):
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", name))


class DBSkillSource(SkillSource):
    """SkillSource backed by the user's DB-stored skills."""

    def __init__(self, repo: "UserSkillRepository", user_id: UUID) -> None:
        self._repo = repo
        self._user_id = user_id

    def list_metadata(self) -> list[AiSkill]:
        rows = self._repo.list_by_user(self._user_id)
        return [AiSkill(name=r.name, description=r.description) for r in rows]

    def load_content(self, name: str) -> str | None:
        return self._repo.get_content_by_name(self._user_id, name)


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
