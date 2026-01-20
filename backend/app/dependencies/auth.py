"""Authentication dependencies for FastAPI."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi_nextauth_jwt import NextAuthJWTv4

from app.config import settings

# Initialize NextAuth JWT dependency
JWT = NextAuthJWTv4(secret=settings.auth_secret)


def get_current_user(jwt: Annotated[dict, Depends(JWT)]) -> dict:
    """
    Dependency to get current authenticated user from JWT.
    
    Raises HTTPException if user is not authenticated.
    """
    if not jwt:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    # Extract user information from JWT
    # NextAuth v4 stores user ID in 'sub' field, and may also have it in user object
    user_id = jwt.get("sub")
    if not user_id and "user" in jwt:
        user_id = jwt["user"].get("id") or jwt["user"].get("sub")
    
    email = jwt.get("email")
    if not email and "user" in jwt:
        email = jwt["user"].get("email")
    
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    # Convert user_id to string if it's not already
    user_id_str = str(user_id)
    
    return {
        "id": user_id_str,
        "email": email,
        "name": jwt.get("name") or (jwt.get("user", {}).get("name") if "user" in jwt else None),
    }
