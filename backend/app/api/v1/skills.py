"""Skills API endpoints (user-owned skills: list, get, update, delete)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.domain.skill.schemas import (
    UserSkillListResponse,
    UserSkillResponse,
    UserSkillUpdateRequest,
)
from app.domain.skill.service import SkillService
from app.domain.user import User

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=UserSkillListResponse)
async def list_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List current user's skills (full objects including content)."""
    service = SkillService(db=db)
    skills = service.get_user_skills(current_user.id)
    return UserSkillListResponse(skills=[UserSkillResponse(**s) for s in skills])


@router.get("/{skill_id}", response_model=UserSkillResponse)
async def get_skill(
    skill_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get one skill by id. Returns 404 if not found or not owned by user."""
    service = SkillService(db=db)
    skill = service.get_user_skill_by_id(current_user.id, skill_id)
    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    return UserSkillResponse(**skill)


@router.patch("/{skill_id}", response_model=UserSkillResponse)
async def update_skill(
    skill_id: UUID,
    body: UserSkillUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update description and/or content by id. Returns 404 if not found."""
    service = SkillService(db=db)
    ok = service.update_user_skill_by_id(
        current_user.id,
        skill_id,
        description=body.description,
        content=body.content,
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    skill = service.get_user_skill_by_id(current_user.id, skill_id)
    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    return UserSkillResponse(**skill)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete skill by id. Returns 404 if not found."""
    service = SkillService(db=db)
    ok = service.delete_user_skill_by_id(current_user.id, skill_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    return None
