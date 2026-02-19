"""Skill API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.skill.repository import UserSkillRepository, _validate_skill_name
from src.skill.schemas import SkillCreate, SkillResponse, SkillUpdate
from src.user.models import User

router = APIRouter(prefix="/skills", tags=["skills"])


def _validate_skill_name_or_raise(name: str) -> None:
    """Validate skill name; raise HTTPException if invalid."""
    if not _validate_skill_name(name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Name must be 1-64 characters, lowercase letters, numbers, "
                "and hyphens only (e.g. my-skill)"
            ),
        )


@router.get("", response_model=list[SkillResponse])
def list_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List current user's skills (user skills only)."""
    repo = UserSkillRepository(db)
    rows = repo.list_by_user(current_user.id)
    return [SkillResponse.model_validate(r) for r in rows]


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(
    skill_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get one skill by id."""
    repo = UserSkillRepository(db)
    row = repo.get_by_id(skill_id, current_user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return SkillResponse.model_validate(row)


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    body: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new skill."""
    _validate_skill_name_or_raise(body.name)
    repo = UserSkillRepository(db)
    row = repo.create(
        current_user.id,
        body.name,
        body.description or "",
        body.content or "",
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Skill with this name already exists",
        )
    return SkillResponse.model_validate(row)


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: UUID,
    body: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a skill."""
    if body.name is not None:
        _validate_skill_name_or_raise(body.name)
    repo = UserSkillRepository(db)
    row = repo.update(
        skill_id,
        current_user.id,
        name=body.name,
        description=body.description,
        content=body.content,
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found or name conflicts with existing skill",
        )
    return SkillResponse.model_validate(row)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a skill."""
    repo = UserSkillRepository(db)
    if not repo.delete(skill_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
