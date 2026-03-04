from fastmcp import FastMCP
from pathlib import Path

from workspace import get_workspace_root, resolve_under_root

mcp = FastMCP("Files")

WORKSPACE = get_workspace_root()

DEFAULT_IGNORE = [
    "node_modules/",
    ".git/",
    "__pycache__/",
    "dist/",
    "build/",
    "target/",
    "vendor/",
    ".venv/",
    "venv/",
]


@mcp.tool
def read_file(
    path: str,
    offset: int = 0,
    limit: int = 2000,
    max_line_length: int = 2000,
) -> str:
    """Read a file or slice of it with line numbers. Path is relative to workspace."""
    resolved = resolve_under_root(WORKSPACE, path)
    if resolved is None:
        return "Path not allowed."
    if not resolved.is_file():
        return "File not found."
    try:
        content = resolved.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return f"Error reading file: {e}"
    lines = content.splitlines()
    if offset < 0:
        offset = 0
    if limit <= 0:
        limit = 2000
    slice_lines = lines[offset : offset + limit]
    out = []
    for i, line in enumerate(slice_lines, start=offset + 1):
        if len(line) > max_line_length:
            line = line[: max_line_length - 3] + "..."
        out.append(f"{i:6}| {line}")
    return "\n".join(out) if out else "(empty slice)"


@mcp.tool
def list_dir(
    path: str,
    max_entries: int = 100,
    ignore: list[str] | None = None,
) -> str:
    """List directory contents as a tree. Path is relative to workspace. Use ignore to skip dirs (e.g. node_modules/)."""
    resolved = resolve_under_root(WORKSPACE, path)
    if resolved is None:
        return "Path not allowed."
    if not resolved.is_dir():
        return "Not a directory."
    patterns = set(DEFAULT_IGNORE)
    if ignore:
        patterns.update(p.strip() for p in ignore if p.strip())
    entries_list: list[str] = []
    count = [0]

    def walk(p: Path, prefix: str) -> None:
        if count[0] >= max_entries:
            return
        try:
            children = sorted(
                p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
            )
        except OSError:
            return
        for i, child in enumerate(children):
            if count[0] >= max_entries:
                entries_list.append(f"{prefix}... (max_entries reached)")
                return
            name = child.name
            skip = any(name == pat.rstrip("/") for pat in patterns)
            if skip:
                continue
            count[0] += 1
            marker = "/" if child.is_dir() else ""
            entries_list.append(f"{prefix}{name}{marker}")
            if child.is_dir():
                walk(child, prefix + "  ")

    walk(resolved, "")
    return "\n".join(entries_list) if entries_list else "(empty)"


@mcp.tool
def edit_file(
    path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
) -> str:
    """Replace old_string with new_string in file (exact match). Set replace_all to replace every occurrence."""
    resolved = resolve_under_root(WORKSPACE, path)
    if resolved is None:
        return "Path not allowed."
    if not resolved.is_file():
        return "File not found."
    try:
        content = resolved.read_text(encoding="utf-8")
    except OSError as e:
        return f"Error reading file: {e}"
    if old_string not in content:
        return "old_string not found."
    if replace_all:
        new_content = content.replace(old_string, new_string)
    else:
        new_content = content.replace(old_string, new_string, 1)
    try:
        resolved.write_text(new_content, encoding="utf-8")
    except OSError as e:
        return f"Error writing file: {e}"
    return "Updated."


@mcp.tool
def write_file(path: str, content: str) -> str:
    """Write content to a file (creates or overwrites). Path is relative to workspace."""
    resolved = resolve_under_root(WORKSPACE, path)
    if resolved is None:
        return "Path not allowed."
    try:
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
    except OSError as e:
        return f"Error writing file: {e}"
    return "Written."
