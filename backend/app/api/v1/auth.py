"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.domain.user import (
    SignupRequest,
    SignupResponse,
    TokenRequest,
    TokenResponse,
    User,
    UserResponse,
)
from app.domain.user.service import UserService

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
    user_service = UserService(db)

    try:
        user_service.signup(request)
        return SignupResponse(success=True)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        ) from e


@router.post("/token", response_model=TokenResponse)
async def login(
    request: TokenRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate user and return JWT token.

    Args:
        request: TokenRequest containing email and password
        db: Database session dependency

    Returns:
        TokenResponse: JWT access token and token type

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    user_service = UserService(db)

    try:
        access_token = user_service.login(request)
        return TokenResponse(access_token=access_token, token_type="bearer")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user from JWT token

    Returns:
        UserResponse: User data (id, name, email, created_at, updated_at)

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    return current_user
