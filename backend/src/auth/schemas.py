"""Auth schemas for API requests and responses."""

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


class TokenRequest(BaseModel):
    """Token request schema for user login."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class TokenResponse(BaseModel):
    """Token response schema for authentication."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
