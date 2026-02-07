"""Request-scoped context (contextvars) for user and DB session.

Used so tools invoked during chat streaming can access the current user
and database session without passing them through the agent call stack.
"""

from contextlib import contextmanager
from contextvars import ContextVar
from uuid import UUID

from sqlalchemy.orm import Session

_current_user_id: ContextVar[UUID | None] = ContextVar("current_user_id", default=None)
_current_db: ContextVar[Session | None] = ContextVar("current_db", default=None)


def get_current_user_id() -> UUID | None:
    """Return the current request's user id, or None if not set."""
    return _current_user_id.get()


def set_current_user_id(user_id: UUID | None) -> None:
    """Set the current request's user id."""
    _current_user_id.set(user_id)


def get_current_db() -> Session | None:
    """Return the current request's database session, or None if not set."""
    return _current_db.get()


def set_current_db(db: Session | None) -> None:
    """Set the current request's database session."""
    _current_db.set(db)


@contextmanager
def request_context(user_id: UUID | None = None, db: Session | None = None):
    """Context manager that sets current user id and db for the request.

    Clears both on exit so the context does not leak to other requests.
    """
    token_user = _current_user_id.set(user_id)
    token_db = _current_db.set(db)
    try:
        yield
    finally:
        _current_user_id.reset(token_user)
        _current_db.reset(token_db)
