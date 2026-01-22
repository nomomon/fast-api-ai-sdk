"""Authentication utilities for JWT token handling."""

from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.models.user import User

security = HTTPBearer()


def create_access_token(user: User) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user: User object containing user information

    Returns:
        str: Encoded JWT token
    """
    expire = datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
    to_encode = {
        "sub": str(user.id),
        "name": user.name,
        "email": user.email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> UUID | None:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        UUID | None: User ID if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return UUID(user_id)
    except (JWTError, ValueError):
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency function to get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session dependency

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials
    user_id = verify_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
