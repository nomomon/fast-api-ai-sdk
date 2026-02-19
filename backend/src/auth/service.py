"""Auth service - JWT creation and auth orchestration."""

from datetime import datetime, timedelta

from jose import jwt

from src.auth.config import auth_settings
from src.user.models import User


def create_access_token(user: User) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user: User object containing user information

    Returns:
        str: Encoded JWT token
    """
    expire = datetime.utcnow() + timedelta(days=auth_settings.jwt_exp_days)
    to_encode = {
        "sub": str(user.id),
        "name": user.name,
        "email": user.email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    encoded_jwt = jwt.encode(
        to_encode,
        auth_settings.secret_key,
        algorithm=auth_settings.algorithm,
    )
    return encoded_jwt
