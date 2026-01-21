"""User routes for API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.user import AuthUserResponse, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a specific user by ID.

    Args:
        user_id: UUID of the user to fetch
        db: Database session dependency

    Returns:
        UserResponse: User data

    Raises:
        HTTPException: 404 if user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


@router.get("/email/{email}", response_model=AuthUserResponse)
async def get_user_by_email(
    email: EmailStr,
    db: Session = Depends(get_db),
):
    """
    Get a user by email address.

    This endpoint returns the user including the password hash for NextAuth verification.
    Should only be called from server-side code (NextJS server actions).

    Args:
        email: Email address of the user to fetch
        db: Database session dependency

    Returns:
        AuthUserResponse: User data including password hash

    Raises:
        HTTPException: 404 if user not found
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found",
        )
    return user
