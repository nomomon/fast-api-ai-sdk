"""JWT authentication utilities."""

from datetime import datetime, timedelta

from jose import jwt

from app.core.config import settings
from app.domain.user.models import User


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
