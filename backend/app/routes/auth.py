"""Authentication routes for API endpoints."""

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.user import SignupRequest, SignupResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user.

    Args:
        request: SignupRequest containing name, email, and password
        db: Database session dependency

    Returns:
        SignupResponse: Success status or error message

    Raises:
        HTTPException: 409 if user already exists, 500 for server errors
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    # Hash password using bcrypt (10 rounds, matching bcryptjs default)
    hashed_password = bcrypt.hashpw(
        request.password.encode("utf-8"),
        bcrypt.gensalt(rounds=10),
    ).decode("utf-8")

    try:
        # Create new user
        new_user = User(
            name=request.name,
            email=request.email,
            password=hashed_password,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return SignupResponse(success=True)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )
