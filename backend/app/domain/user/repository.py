"""User repository for data access."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.user.models import User


class UserRepository:
    """Repository for user data access operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        """Get user by email.

        Args:
            email: User email address

        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user: User) -> User:
        """Create a new user.

        Args:
            user: User object to create

        Returns:
            Created user object
        """
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def email_exists(self, email: str) -> bool:
        """Check if email already exists.

        Args:
            email: Email address to check

        Returns:
            True if email exists, False otherwise
        """
        return self.db.query(User).filter(User.email == email).first() is not None
