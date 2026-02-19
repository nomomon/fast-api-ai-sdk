"""User service for business logic."""

import bcrypt
from sqlalchemy.orm import Session

from src.auth.schemas import SignupRequest, TokenRequest
from src.user.models import User
from src.user.repository import UserRepository


class UserService:
    """Service for user business logic."""

    def __init__(self, db: Session):
        """Initialize service with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.repository = UserRepository(db)

    def signup(self, request: SignupRequest) -> User:
        """Register a new user.

        Args:
            request: Signup request data

        Returns:
            Created user object

        Raises:
            ValueError: If user already exists
        """
        if self.repository.email_exists(request.email):
            raise ValueError("User with this email already exists")

        # Hash password using bcrypt
        hashed_password = bcrypt.hashpw(
            request.password.encode("utf-8"),
            bcrypt.gensalt(rounds=10),
        ).decode("utf-8")

        new_user = User(
            name=request.name,
            email=request.email,
            password=hashed_password,
        )

        return self.repository.create(new_user)

    def login(self, request: TokenRequest) -> User:
        """Authenticate user and return user object.

        Args:
            request: Login request data

        Returns:
            Authenticated user object

        Raises:
            ValueError: If credentials are invalid
        """
        user = self.repository.get_by_email(request.email)
        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        try:
            password_valid = bcrypt.checkpw(
                request.password.encode("utf-8"),
                user.password.encode("utf-8"),
            )
        except Exception:
            raise ValueError("Invalid email or password") from None

        if not password_valid:
            raise ValueError("Invalid email or password")

        return user
