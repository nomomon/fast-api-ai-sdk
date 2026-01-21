"""Database session dependency for FastAPI."""

from sqlalchemy.orm import Session

from app.database.base import SessionLocal


def get_db() -> Session:
    """
    Dependency function that provides a database session.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
