"""Repository functions for database operations."""

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import User


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email address."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, name: str, email: str, hashed_password: str) -> User:
    """Create a new user."""
    user = User(name=name, email=email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
