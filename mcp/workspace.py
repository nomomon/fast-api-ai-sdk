"""Workspace root and path safety for MCP file tools."""

import os
from pathlib import Path


def get_workspace_root() -> Path:
    """Return the workspace root directory (from WORKSPACE_ROOT env or default /app)."""
    raw = os.environ.get("WORKSPACE_ROOT", "/app")
    root = Path(raw).resolve()
    if not root.is_dir():
        root = Path("/app").resolve()
        if not root.is_dir():
            root = Path.cwd()
    return root


def resolve_under_root(workspace_root: Path, path: str) -> Path | None:
    """Resolve path under workspace_root; return None if path escapes the root."""
    if not path or path.strip() != path:
        return None
    # Normalize: strip leading slash so we don't treat as absolute
    normalized = path.strip().lstrip("/")
    if ".." in normalized:
        return None
    try:
        resolved = (workspace_root / normalized).resolve()
        root_resolved = workspace_root.resolve()
        # Ensure resolved is under root (same path or a subpath)
        try:
            common = os.path.commonpath([str(resolved), str(root_resolved)])
        except ValueError:
            return None
        if common != str(root_resolved):
            return None
        # Resolved must equal root or be a strict subpath (root + sep + something)
        if resolved != root_resolved and not str(resolved).startswith(
            str(root_resolved) + os.sep
        ):
            return None
        return resolved
    except Exception:
        return None
