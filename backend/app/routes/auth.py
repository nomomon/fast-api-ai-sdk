"""Authentication routes for user management."""

from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.db import get_db, repository
from app.dependencies.auth import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()


class SignupRequest(BaseModel):
    """Request model for user signup."""

    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Request model for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response model for user data."""

    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


@router.get("/auth/user-exists/{email}")
async def check_user_exists(
    email: str,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Check if a user exists by email (public endpoint for OAuth flows).
    
    Returns a boolean indicating if the user exists.
    """
    user = repository.get_user_by_email(db, email)
    return {"exists": user is not None}


@router.post("/auth/login", response_model=UserResponse)
async def login(
    request: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Verify user credentials and return user data.
    
    Used by NextAuth credentials provider.
    """
    # Get user by email
    user = repository.get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    is_valid = bcrypt.checkpw(
        request.password.encode("utf-8"), user.password.encode("utf-8")
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return UserResponse(id=user.id, name=user.name, email=user.email)


@router.post("/auth/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Create a new user account.
    
    Returns the created user without password.
    """
    # Check if user already exists
    existing_user = repository.get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Hash password
    hashed_password = bcrypt.hashpw(request.password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    # Create user
    user = repository.create_user(db, request.name, request.email, hashed_password)

    return UserResponse(id=user.id, name=user.name, email=user.email)


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Get current authenticated user information.
    
    Requires authentication via JWT.
    """
    # Get user from database
    # Try to get by ID first, then fall back to email
    user = None
    try:
        user_id = int(current_user["id"])
        user = repository.get_user_by_id(db, user_id)
    except (ValueError, KeyError):
        pass
    
    if not user:
        # Fall back to email lookup
        user = repository.get_user_by_email(db, current_user["email"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(id=user.id, name=user.name, email=user.email)
