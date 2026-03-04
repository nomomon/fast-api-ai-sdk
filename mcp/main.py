from fastmcp import FastMCP
import contextlib
import io
import traceback


mcp = FastMCP("Demo 🚀")


@mcp.tool
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

if __name__ == "__main__":
    # Bind to 0.0.0.0 so other containers (e.g. backend) can reach this server
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        path="/mcp",
    )