"""User schemas for API requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Signup request schema for user registration."""

    name: str = Field(..., min_length=1, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")


class SignupResponse(BaseModel):
    """Signup response schema."""

    success: bool
    error: str | None = None


class UserResponse(BaseModel):
    """User response schema for API responses."""

    id: UUID
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class AuthUserResponse(BaseModel):
    """User response schema for authentication (includes password hash for NextAuth)."""

    id: UUID
    name: str
    email: EmailStr
    password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
