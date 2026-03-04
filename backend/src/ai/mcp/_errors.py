"""Helpers for surfacing MCP connection errors (e.g. unwrap TaskGroup)."""


def format_mcp_error(exc: BaseException) -> str:
    """Return a user-facing error string, unwrapping TaskGroup/ExceptionGroup."""
    # BaseExceptionGroup (Python 3.11+) and anyio TaskGroup wrap the real cause
    sub = getattr(exc, "exceptions", None)
    if sub:
        first = sub[0]
        if isinstance(first, BaseException):
            return format_mcp_error(first) if getattr(first, "exceptions", None) else str(first)
    return str(exc)
