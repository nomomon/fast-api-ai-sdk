import contextlib
import io
import subprocess
import traceback

from workspace import get_workspace_root

WORKSPACE = get_workspace_root()


def run_python(code: str) -> str:
    """Execute arbitrary Python code and return its output or error."""
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            exec(code, {})
        output = buffer.getvalue()
        return output if output else "Code executed with no output."
    except Exception:
        return "Error while executing code:\n" + traceback.format_exc()


def run_bash(command: str, timeout_seconds: int = 120) -> str:
    """Run a bash command in the workspace directory. Returns combined stdout and stderr."""
    if timeout_seconds <= 0 or timeout_seconds > 120:
        timeout_seconds = 120
    try:
        r = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        out = (r.stdout or "").strip()
        err = (r.stderr or "").strip()
        if err:
            out = f"{out}\n{err}" if out else err
        return out or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout_seconds}s."
    except Exception as e:
        return f"Error: {e}"
